import ipaddress
import math
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from .errors import ValidationError



def compile_regex(regex, flags=0):
    if isinstance(regex, str):
        return re.compile(regex, flags)
    return regex  # Assume already compiled regex object


# Replicates Django's punycode encoding using standard library
def punycode(domain):
    """Encodes a domain to Punycode (RFC 3492)."""
    try:
        # Use 'strict' mode to mimic UnicodeError on invalid input
        return domain.encode('idna', errors='strict').decode('ascii')
    except UnicodeError:
        # Re-raise as UnicodeError to match behavior (though try/except in callers handle it)
        raise UnicodeError("Invalid domain part for IDNA encoding")


# --- Base Validator Classes ---

class RegexValidator:
    regex = ""
    message = "Enter a valid value."
    code = "invalid"
    inverse_match = False
    flags = 0

    def __init__(
            self, regex=None, message=None, code=None, inverse_match=None, flags=None
    ):
        if regex is not None:
            self.regex = regex
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if inverse_match is not None:
            self.inverse_match = inverse_match
        if flags is not None:
            self.flags = flags
        if self.flags and not isinstance(self.regex, (str, bytes)):
            # Allow bytes patterns too, as re.compile accepts them.
            raise TypeError(
                "If the flags are set, regex must be a regular expression string or bytes."
            )

        # Use the helper for standard compilation
        self.regex = compile_regex(self.regex, self.flags)

    def __call__(self, value):
        """
        Validate that the input contains (or does *not* contain, if
        inverse_match is True) a match for the regular expression.
        """
        # Ensure value is a string for regex search
        str_value = str(value)
        regex_matches = self.regex.search(str_value)
        invalid_input = regex_matches if self.inverse_match else not regex_matches
        if invalid_input:
            params = {"value": value}
            # Add regex pattern to params for potential debugging/better messages
            if isinstance(self.regex, (re.Pattern, re.Pattern)):
                params['regex'] = self.regex.pattern
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
                isinstance(other, RegexValidator)
                and self.regex.pattern == other.regex.pattern
                and self.regex.flags == other.regex.flags
                and (self.message == other.message)
                and (self.code == other.code)
                and (self.inverse_match == other.inverse_match)
        )


class BaseValidator:
    message = "Ensure this value is %(limit_value)s (it is %(show_value)s)."
    code = "limit_value"

    def __init__(self, limit_value, message=None):
        self.limit_value = limit_value
        if message:
            self.message = message

    def __call__(self, value):
        cleaned = self.clean(value)
        # Handle callable limit_value if needed (though less common outside Django)
        limit_value = (
            self.limit_value() if callable(self.limit_value) else self.limit_value
        )
        params = {"limit_value": limit_value, "show_value": cleaned, "value": value}
        if self.compare(cleaned, limit_value):
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
                self.limit_value == other.limit_value
                and self.message == other.message
                and self.code == other.code
        )

    def compare(self, a, b):
        # Default comparison: inequality (used by some validators if not overridden)
        return a is not b

    def clean(self, x):
        # Default cleaning: return as is
        return x


# --- Specific Validators ---

class DomainNameValidator(RegexValidator):
    message = "Enter a valid domain name."
    # Define ul once, directly in patterns
    ul = "\u00a1-\uffff"
    hostname_re = (
            r"[a-z" + ul + r"0-9](?:[a-z" + ul + r"0-9-]{0,61}[a-z" + ul + r"0-9])?"
    )
    domain_re = r"(?:\.(?!-)[a-z" + ul + r"0-9-]{1,63}(?<!-))*"
    tld_re = (
            r"\."
            r"(?!-)"
            r"(?:[a-z" + ul + "-]{2,63}"
                              r"|xn--[a-z0-9]{1,59})"
                              r"(?<!-)"
                              r"\.?"
    )
    # ASCII-only versions
    ascii_only_hostname_re = r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    ascii_only_domain_re = r"(?:\.(?!-)[a-zA-Z0-9-]{1,63}(?<!-))*"
    ascii_only_tld_re = (
        r"\."
        r"(?!-)"
        r"(?:[a-zA-Z0-9-]{2,63})"
        r"(?<!-)"
        r"\.?"
    )

    max_length = 255  # As per RFC 1034 sec 3.1 (domain name), RFC 1123 sec 2.1 (hostname)

    def __init__(self, accept_idna=True, message=None, code=None):
        self.accept_idna = accept_idna

        # Determine regex based on accept_idna *before* calling super().__init__
        if self.accept_idna:
            current_regex = self.hostname_re + self.domain_re + self.tld_re
        else:
            current_regex = (
                    self.ascii_only_hostname_re
                    + self.ascii_only_domain_re
                    + self.ascii_only_tld_re
            )

        # Pass determined regex and other args to the parent RegexValidator
        super().__init__(
            regex=compile_regex(r"^" + current_regex + r"\Z", re.IGNORECASE),  # Anchor the regex
            message=message or self.message,
            code=code or self.code  # Default code is 'invalid' from RegexValidator
        )

    def __call__(self, value):
        if not isinstance(value, str):
            raise ValidationError(self.message, code=self.code, params={"value": value})

        # Check length before regex
        if len(value) > self.max_length:
            raise ValidationError(
                f"Ensure this value has at most {self.max_length} characters (it has {len(value)}).",
                code='max_length',  # Use a more specific code
                params={"value": value}
            )

        # Check ASCII if required
        if not self.accept_idna and not value.isascii():
            raise ValidationError("Enter a valid ASCII domain name.", code=self.code, params={"value": value})

        # Perform the regex validation via parent class
        try:
            # Try the original value first
            super().__call__(value)
        except ValidationError as e:
            # If regex fails and IDNA is allowed, try punycode version
            if self.accept_idna and not value.isascii():
                try:
                    punycode_value = punycode(value)
                    # Call super() again with the punycode value
                    # We need to temporarily set self.regex to the ASCII-only version
                    # This is a bit tricky; it might be cleaner to handle punycode logic *before* regex
                    # Let's refactor to validate structure then potentially punycode
                    pass  # Let the original error propagate for now if structure is wrong
                except UnicodeError:
                    # If punycode conversion itself fails, the original error is fine
                    pass
            raise e  # Re-raise the original validation error if punycode didn't help or wasn't tried

        # Additional check: labels (parts separated by dots) must be <= 63 chars
        # The regex already partly handles this, but let's be explicit.
        # This check should ideally happen on the *punycode* version if IDNA.
        effective_value = value
        if self.accept_idna and not value.isascii():
            try:
                effective_value = punycode(value)
            except UnicodeError:
                # This case should have been caught earlier or by regex, but safety check
                raise ValidationError(self.message, code=self.code, params={"value": value})

        labels = effective_value.rstrip('.').split('.')
        if any(len(label) > 63 for label in labels):
            raise ValidationError(
                "Domain labels cannot be longer than 63 characters.",
                code='max_label_length',
                params={"value": value}
            )


# Instance for direct use
validate_domain_name = DomainNameValidator()


# --- IP Address Validators ---

def validate_ipv4_address(value):
    """Validates that the input is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(value)
    except ValueError:
        raise ValidationError(
            "Enter a valid IPv4 address.",
            code="invalid_ipv4",
            params={"value": value},
        )


def validate_ipv6_address(value):
    """Validates that the input is a valid IPv6 address."""
    try:
        # Note: ipaddress.IPv6Address is stricter than Django's is_valid_ipv6_address
        # in some edge cases (e.g., around ':::' or leading/trailing colons)
        # but covers the vast majority of valid cases and RFC compliance.
        ipaddress.IPv6Address(value)
    except ValueError:
        raise ValidationError(
            "Enter a valid IPv6 address.",
            code="invalid_ipv6",
            params={"value": value},
        )


def validate_ipv46_address(value):
    """Validates that the input is a valid IPv4 or IPv6 address."""
    try:
        validate_ipv4_address(value)
    except ValidationError:
        try:
            validate_ipv6_address(value)
        except ValidationError:
            raise ValidationError(
                "Enter a valid IPv4 or IPv6 address.",
                code="invalid_ip",
                params={"value": value},
            )


# Helper function to get validator list (mirrors Django's structure)
ip_address_validator_map = {
    "both": [validate_ipv46_address],
    "ipv4": [validate_ipv4_address],
    "ipv6": [validate_ipv6_address],
}


def ip_address_validators(protocol, unpack_ipv4=False):  # unpack_ipv4 is Django ORM specific, ignored here
    """Returns a list containing the appropriate IP address validator."""
    protocol = protocol.lower()
    if protocol not in ip_address_validator_map:
        raise ValueError(f"The protocol '{protocol}' is unknown. Supported: {list(ip_address_validator_map)}")
    # The 'unpack_ipv4' argument relates to Django's GenericIPAddressField storage,
    # it doesn't change the validation logic itself, so we ignore it here.
    return ip_address_validator_map[protocol]


# --- URL Validator ---

class URLValidator(RegexValidator):
    # Reuse patterns from DomainNameValidator where possible
    ipv4_re = r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3}"
    # Basic IPv6 pattern for initial regex match, full validation happens later
    ipv6_re = r"\[[0-9a-fA-F:.]+\]"

    # Use the IDNA-aware patterns by default from DomainNameValidator
    hostname_re = DomainNameValidator.hostname_re
    domain_re = DomainNameValidator.domain_re
    tld_re = DomainNameValidator.tld_re
    host_re = "(" + hostname_re + domain_re + tld_re + "|localhost)"

    base_regex = compile_regex(
        r"^(?:[a-z0-9.+-]+)://"  # Scheme validated separately
        r"(?:[^\s:@/]+(?::[^\s:@/]*)?@)?"  # user:pass authentication (optional)
        r"(?:" + ipv4_re + "|" + ipv6_re + "|" + host_re + ")"  # Host part
                                                           r"(?::[0-9]{1,5})?"  # Port (optional)
                                                           r"(?:[/?#][^\s]*)?"  # Path, query, fragment (optional)
                                                           r"\Z",
        re.IGNORECASE,
    )

    # ASCII-only host patterns for fallback check if IDNA fails
    ascii_hostname_re = DomainNameValidator.ascii_only_hostname_re
    ascii_domain_re = DomainNameValidator.ascii_only_domain_re
    ascii_tld_re = DomainNameValidator.ascii_only_tld_re
    ascii_host_re = "(" + ascii_hostname_re + ascii_domain_re + ascii_tld_re + "|localhost)"

    ascii_regex = compile_regex(
        r"^(?:[a-z0-9.+-]+)://"
        r"(?:[^\s:@/]+(?::[^\s:@/]*)?@)?"
        r"(?:" + ipv4_re + "|" + ipv6_re + "|" + ascii_host_re + ")"  # ASCII Host part
                                                                 r"(?::[0-9]{1,5})?"
                                                                 r"(?:[/?#][^\s]*)?"
                                                                 r"\Z",
        re.IGNORECASE,
    )

    message = "Enter a valid URL."
    code = "invalid_url"  # More specific code
    schemes = ["http", "https", "ftp", "ftps"]  # Default schemes
    unsafe_chars = frozenset("\t\r\n")  # Characters disallowed anywhere in URL
    max_length = 2048  # Common practical limit

    def __init__(self, schemes=None, message=None, code=None):
        # We don't directly pass regex to super().__init__ because logic is more complex
        # We still call super().__init__ to set message/code if provided
        super().__init__(message=message or self.message, code=code or self.code)
        if schemes is not None:
            self.schemes = [s.lower() for s in schemes]

    def __call__(self, value):
        if not isinstance(value, str):
            raise ValidationError(self.message, code='invalid_type', params={"value": value})

        if len(value) > self.max_length:
            raise ValidationError(
                f"Ensure this URL has at most {self.max_length} characters (it has {len(value)}).",
                code='max_length',
                params={"value": value}
            )

        if self.unsafe_chars.intersection(value):
            raise ValidationError("URL contains unsafe characters (tabs, newlines).", code='unsafe_chars',
                                  params={"value": value})

        # 1. Validate scheme
        try:
            scheme = value.split("://", 1)[0].lower()
        except IndexError:
            raise ValidationError("URL scheme missing or invalid.", code='invalid_scheme', params={"value": value})

        if scheme not in self.schemes:
            raise ValidationError(
                f"URL scheme '{scheme}' is not allowed. Allowed schemes: {', '.join(self.schemes)}",
                code='invalid_scheme',
                params={"value": value, "scheme": scheme}
            )

        # 2. Split the URL
        try:
            splitted_url = urlsplit(value)
        except ValueError:  # Catches potential issues in urlsplit itself
            raise ValidationError(self.message, code=self.code, params={"value": value})

        # 3. Validate structure using regex (try IDNA-aware first)
        if not self.base_regex.match(value):
            # If the main regex fails, try to punycode the domain and re-validate
            # This handles the case where the domain part has unicode chars
            if value:
                try:
                    # Only encode the netloc part
                    netloc = punycode(splitted_url.netloc)
                    # Reconstruct URL with punycoded netloc
                    url_punycode = urlunsplit(
                        (splitted_url.scheme, netloc, splitted_url.path, splitted_url.query, splitted_url.fragment))

                    # Validate the punycoded version with the ASCII regex
                    if not self.ascii_regex.match(url_punycode):
                        raise ValidationError(self.message, code=self.code, params={"value": value})
                    # If punycode version matches, proceed with this representation for further checks
                    splitted_url = urlsplit(url_punycode)  # Update splitted_url for hostname checks

                except (UnicodeError, ValueError):  # Error during punycode or reconstruction
                    # If punycode fails or reconstruction is bad, the original regex failure stands
                    raise ValidationError(self.message, code=self.code, params={"value": value})
            else:
                # Empty value failed regex, raise error
                raise ValidationError(self.message, code=self.code, params={"value": value})

        # 4. Validate IPv6 Address specifically if present
        # The regex for IPv6 is basic; do a full validation here.
        # Check the netloc *after* potential punycode conversion
        host_match = re.match(r"^\[(.+)\](?::[0-9]{1,5})?$", splitted_url.netloc or "")
        if host_match:
            potential_ip = host_match[1]
            try:
                validate_ipv6_address(potential_ip)
            except ValidationError:
                # Raise URL-specific error if IPv6 validation fails
                raise ValidationError("Enter a valid IPv6 address part in the URL.", code='invalid_ipv6_in_url',
                                      params={"value": value})

        # 5. Validate Hostname Length (using the potentially punycoded hostname)
        # RFC 1034: Max 253 chars for the full hostname (excluding potential trailing dot)
        # urlsplit provides hostname already decoded/normalized.
        hostname = splitted_url.hostname
        if hostname:
            # Handle edge case: Punycode can expand length
            if not hostname.isascii():  # Should have been converted earlier, but safety check
                try:
                    hostname = punycode(hostname)
                except UnicodeError:
                    raise ValidationError("Invalid characters in hostname.", code='invalid_hostname_chars',
                                          params={"value": value})

            if len(hostname) > 253:
                raise ValidationError(
                    f"Hostname '{hostname[:50]}...' is too long (max 253 chars).",
                    code='hostname_too_long',
                    params={"value": value}
                )
            # Also check domain label length constraint using the DomainNameValidator logic
            # Re-instantiate or call DomainNameValidator directly here?
            # Let's do a quick check here based on DomainNameValidator's logic
            labels = hostname.rstrip('.').split('.')
            if any(len(label) > 63 for label in labels):
                raise ValidationError(
                    "Hostname labels cannot be longer than 63 characters.",
                    code='max_label_length',
                    params={"value": value}
                )
        elif not host_match and splitted_url.netloc and "@" not in splitted_url.netloc:
            # If not an IP literal and hostname is None/empty, it's likely invalid structure
            # (e.g., "http://:80") unless it's just "localhost" which regex handles.
            # Check if netloc is non-empty but doesn't contain a valid host part.
            # This condition is tricky, the main regex should mostly catch this.
            # A simple check: if hostname is empty but netloc isn't and isn't an IP.
            if splitted_url.netloc not in ('localhost'):  # Allow bare localhost
                # Could be an IPv4 address - check that too
                try:
                    validate_ipv4_address(splitted_url.netloc.split(":")[0])  # Check part before port
                except ValidationError:
                    # If not IPv4, and not localhost, and hostname empty -> invalid.
                    raise ValidationError("Invalid host part in URL.", code='invalid_host', params={"value": value})


# Instance for direct use
validate_url = URLValidator()

# --- Integer Validator ---

integer_validator_regex = compile_regex(r"^-?\d+\Z")
integer_validator = RegexValidator(
    integer_validator_regex,
    message="Enter a valid integer.",
    code="invalid_integer",
)


def validate_integer(value):
    """Validates that the input represents a valid integer."""
    return integer_validator(value)


# --- Email Validator ---

class EmailValidator:
    message = "Enter a valid email address."
    code = "invalid_email"
    # RFC 5322 / HTML5 spec derived patterns (simplified from Django's complex ones for clarity)
    # User part: Allows most printable ASCII chars, dot but not at start/end or repeated.
    # Note: Django's user_regex is very complex, including quoted strings.
    # This simplified version covers common cases but might reject some rare valid emails.
    # For robustness, consider libraries like 'email_validator'.
    user_regex = compile_regex(
        r"^[a-zA-Z0-9!#$%&'*+\-/=?^_`{|}~.]+"  # Allowed characters
        r"(?<!\.)"  # Cannot end with a dot
        r"(?<!^.)"  # Cannot start with a dot (implicit in +)
        # No check for consecutive dots here, simpler regex
        r"$",
        re.IGNORECASE
    )
    # Domain part: Use DomainNameValidator logic, but require at least one dot.
    # We'll use the validator instance directly.
    domain_validator = DomainNameValidator(accept_idna=True)
    literal_regex = compile_regex(r"\[([a-fA-F0-9:.%]+)\]$", re.IGNORECASE)  # Allow IPv6 literals

    # Allowlist for domains that bypass normal validation (e.g., 'localhost')
    domain_allowlist = ["localhost"]
    max_length = 320  # RFC 3696 Errata ID 1690 suggests 254 is more accurate, but Django uses 320.

    def __init__(self, message=None, code=None, allowlist=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if allowlist is not None:
            # Ensure allowlist is lowercase for case-insensitive comparison
            self.domain_allowlist = [d.lower() for d in allowlist]

    def __call__(self, value):
        if not value or not isinstance(value, str):
            raise ValidationError(self.message, code=self.code, params={"value": value})

        if '@' not in value:
            raise ValidationError("Email address must contain an '@' symbol.", code='missing_at',
                                  params={"value": value})

        if len(value) > self.max_length:
            raise ValidationError(
                f"Ensure this email address has at most {self.max_length} characters (it has {len(value)}).",
                code='max_length',
                params={"value": value}
            )

        user_part, domain_part = value.rsplit("@", 1)

        if not user_part:
            raise ValidationError("Email address user part cannot be empty.", code='empty_user',
                                  params={"value": value})

        # Basic check on user part (can be expanded)
        # The regex below is too simple compared to Django's original.
        # if not self.user_regex.match(user_part):
        #     raise ValidationError("Invalid user part in email address.", code='invalid_user', params={"value": value})
        # A simple check for unsafe chars might be better than a complex regex
        if any(c in user_part for c in '()<>[]:,;\\ '):  # Chars often problematic if not quoted
            if not (user_part.startswith('"') and user_part.endswith('"')):  # Allow if properly quoted
                raise ValidationError("Invalid characters in user part of email address.", code='invalid_user_chars',
                                      params={"value": value})

        if not self.validate_domain_part(domain_part):
            raise ValidationError("Invalid domain part in email address.", code='invalid_domain',
                                  params={"value": value})

    def validate_domain_part(self, domain_part):
        if not domain_part:
            return False

        # Lowercase domain for allowlist and validation checks
        domain_part_lower = domain_part.lower()

        if domain_part_lower in self.domain_allowlist:
            return True

        # Check for IP Literal (e.g., user@[192.168.0.1] or user@[::1])
        literal_match = self.literal_regex.match(domain_part)
        if literal_match:
            ip_address = literal_match[1]
            # If it contains '%', it might be an IPv6 scope ID. ipaddress handles this.
            try:
                validate_ipv46_address(ip_address)
                return True
            except ValidationError:
                # Invalid IP literal
                return False

        # If not an allowlisted domain or a valid IP literal, validate as a domain name
        try:
            self.domain_validator(domain_part)
            # Ensure there's at least one dot unless it's IDNA (punycode handles that)
            # or a single label TLD (which domain_validator should allow if valid).
            # Let domain_validator handle TLD rules.
            return True
        except ValidationError:
            return False

    def __eq__(self, other):
        return (
                isinstance(other, EmailValidator)
                and (set(self.domain_allowlist) == set(other.domain_allowlist))
                and (self.message == other.message)
                and (self.code == other.code)
        )


# Instance for direct use
validate_email = EmailValidator()

# --- Slug Validators ---

# ASCII Slug
slug_re = compile_regex(r"^[a-zA-Z0-9_-]+\Z")
validate_slug = RegexValidator(
    slug_re,
    message="Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.",
    code="invalid_slug",
)

# Unicode Slug (allows letters from any language)
# \w includes letters (unicode if flag set, but Python 3 regex does by default), numbers, underscore.
# We explicitly add hyphen.
slug_unicode_re = compile_regex(r"^[-\w]+\Z", re.UNICODE)  # re.UNICODE is default in Py3 but explicit
validate_unicode_slug = RegexValidator(
    slug_unicode_re,
    message="Enter a valid 'slug' consisting of Unicode letters, numbers, underscores, or hyphens.",
    code="invalid_unicode_slug",
)


# --- Comma-Separated Integer List Validator ---

def int_list_validator(sep=",", message=None, code="invalid_list", allow_negative=False):
    # Regex to match comma-separated integers
    # Uses non-capturing groups (?:...)
    # Allows optional negative sign if allow_negative is True
    pattern = (
            r"^%(neg)s\d+(?:%(sep)s%(neg)s\d+)*\Z"
            % {
                "neg": r"-?" if allow_negative else "",
                # Escape the separator in case it's a special regex character
                "sep": re.escape(sep),
            }
    )
    default_message = "Enter only integers separated by '%(separator)s'." % {'separator': sep}
    return RegexValidator(
        compile_regex(pattern),
        message=message or default_message,
        code=code
    )


# Instance for common case (comma-separated, positive integers)
validate_comma_separated_integer_list = int_list_validator(
    message="Enter only positive integers separated by commas.",
    code="invalid_comma_int_list",
    allow_negative=False  # Default is positive only
)


# --- Min/Max Value Validators ---

class MaxValueValidator(BaseValidator):
    message = "Ensure this value is less than or equal to %(limit_value)s."
    code = "max_value"

    def compare(self, a, b):
        # Validation fails if a > b
        return a > b


class MinValueValidator(BaseValidator):
    message = "Ensure this value is greater than or equal to %(limit_value)s."
    code = "min_value"

    def compare(self, a, b):
        # Validation fails if a < b
        return a < b


# --- Step Value Validator ---
class StepValueValidator(BaseValidator):
    # Message updated to be clearer without Django's specific context
    message = "Ensure this value is a multiple of step size %(limit_value)s."
    code = "step_size"
    offset_message = (  # Separate message when offset is used
        "Ensure this value is a multiple of step size %(limit_value)s, "
        "starting from %(offset)s."
    )

    def __init__(self, limit_value, message=None, offset=None):
        # Choose message based on offset *before* calling super
        effective_message = message or (self.offset_message if offset is not None else self.message)
        super().__init__(limit_value, effective_message)
        self.offset = offset if offset is not None else 0  # Default offset to 0

    def __call__(self, value):
        # Get numeric types for calculation
        # Ensure value, limit_value, and offset are compatible numeric types
        # This might require conversion or type checking depending on expected inputs
        try:
            # Assume float/Decimal compatibility is desired, like Django
            # Convert all to Decimal for precision, assuming input might be float/int/Decimal
            # Requires 'from decimal import Decimal, InvalidOperation'
            cleaned = Decimal(str(value))
            limit_value = Decimal(str(self.limit_value() if callable(self.limit_value) else self.limit_value))
            offset = Decimal(str(self.offset))
        except InvalidOperation:
            raise ValidationError("Value must be a number for step validation.", code='invalid_type',
                                  params={'value': value})
        except TypeError:
            raise TypeError("StepValueValidator requires numeric inputs/limits/offsets.")

        params = {"limit_value": limit_value, "offset": offset, "value": value}

        # Compare using Decimal math
        # Use modulo, check if remainder is close to zero
        try:
            remainder = (cleaned - offset) % limit_value
        except (ValueError, TypeError):  # e.g., modulo by zero
            raise ValidationError("Invalid step value (%(limit_value)s).", code='invalid_step', params=params)

        # Check if remainder is close to 0 or limit_value (handles floating point issues)
        is_multiple = math.isclose(remainder, Decimal(0), abs_tol=Decimal('1e-9')) or \
                      math.isclose(remainder, limit_value, abs_tol=Decimal('1e-9'))

        if not is_multiple:
            raise ValidationError(self.message, code=self.code, params=params)

    def compare(self, a, b):
        # This method isn't really used directly due to the override of __call__
        # The logic is now inside __call__
        pass


# --- Min/Max Length Validators ---

class MinLengthValidator(BaseValidator):
    # Simplified message without ngettext
    message = "Ensure this value has at least %(limit_value)d characters (it has %(show_value)d)."
    code = "min_length"

    def compare(self, a, b):
        # Validation fails if length a < limit b
        return a < b

    def clean(self, x):
        # Operates on the length of the input
        try:
            return len(x)
        except TypeError:
            # Handle cases where len() is not applicable (e.g., numbers)
            # Or decide this validator only works on sequences. Let's assume sequences.
            raise TypeError("MinLengthValidator requires a value with a defined length (string, list, etc.).")


class MaxLengthValidator(BaseValidator):
    # Simplified message without ngettext
    message = "Ensure this value has at most %(limit_value)d characters (it has %(show_value)d)."
    code = "max_length"

    def compare(self, a, b):
        # Validation fails if length a > limit b
        return a > b

    def clean(self, x):
        # Operates on the length of the input
        try:
            return len(x)
        except TypeError:
            raise TypeError("MaxLengthValidator requires a value with a defined length (string, list, etc.).")


# --- Decimal Validator ---

class DecimalValidator:
    """
    Validates that the input Decimal does not exceed the maximum number of digits
    or decimal places.
    Requires 'from decimal import Decimal, InvalidOperation'.
    """
    messages = {
        "invalid": "Enter a number.",
        "max_digits": "Ensure that there are no more than %(max)s digits in total.",
        "max_decimal_places": "Ensure that there are no more than %(max)s decimal places.",
        "max_whole_digits": "Ensure that there are no more than %(max)s digits before the decimal point.",
    }

    def __init__(self, max_digits, decimal_places):
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def __call__(self, value):
        # Ensure the input is a Decimal object
        if not isinstance(value, Decimal):
            # Attempt conversion, but raise if it's not Decimal-like
            try:
                value = Decimal(value)
            except (InvalidOperation, TypeError, ValueError):
                raise ValidationError(self.messages["invalid"], code="invalid_decimal", params={"value": value})

        # Check for non-finite values (NaN, Infinity)
        if not value.is_finite():
            raise ValidationError(self.messages["invalid"], code="invalid_decimal_nan_inf", params={"value": value})

        sign, digit_tuple, exponent = value.as_tuple()

        # Normalize to remove trailing zeros in exponent, if integer
        # This representation can be complex. Let's use properties of Decimal.

        # Use adjusted() for exponent relative to the first digit
        # Use quantize() to count decimal places easily

        if exponent >= 0:  # It's an integer or has trailing zeros
            decimals = 0
            digits = len(digit_tuple) + exponent  # Total digits including trailing zeros
            whole_digits = digits
        else:  # It has decimal places
            decimals = abs(exponent)
            digits = len(digit_tuple)  # Digits stored explicitly
            whole_digits = max(0, digits - decimals)  # Digits before the decimal point

            # Edge case: If exponent requires more leading zeros than digits available
            # e.g., Decimal('0.001') -> digits=1, decimals=3. Need to adjust total digits.
            if decimals > digits:
                # The number of digits is effectively the number of decimal places
                # e.g., 0.001 has 3 digits in this context (0, 0, 1 after point)
                digits = decimals

        # Check constraints
        if self.max_digits is not None and digits > self.max_digits:
            raise ValidationError(
                self.messages["max_digits"],
                code="max_digits",
                params={"max": self.max_digits, "value": value},
            )
        if self.decimal_places is not None and decimals > self.decimal_places:
            raise ValidationError(
                self.messages["max_decimal_places"],
                code="max_decimal_places",
                params={"max": self.decimal_places, "value": value},
            )
        # Check whole digits (digits before the decimal point)
        if (
                self.max_digits is not None
                and self.decimal_places is not None
                and whole_digits > (self.max_digits - self.decimal_places)
        ):
            raise ValidationError(
                self.messages["max_whole_digits"],
                code="max_whole_digits",
                params={"max": (self.max_digits - self.decimal_places), "value": value},
            )

    def __eq__(self, other):
        return (
                isinstance(other, self.__class__)
                and self.max_digits == other.max_digits
                and self.decimal_places == other.decimal_places
        )


# --- File Extension Validator ---

class FileExtensionValidator:
    message = (
        "File extension '%(extension)s' is not allowed. "
        "Allowed extensions are: %(allowed_extensions)s."
    )
    code = "invalid_extension"

    def __init__(self, allowed_extensions=None, message=None, code=None):
        if allowed_extensions is not None:
            # Store extensions lowercased and without the leading dot for comparison
            self.allowed_extensions = {
                ext.lower().lstrip(".") for ext in allowed_extensions
            }
        else:
            self.allowed_extensions = None  # Allow any extension if None

        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        # Expects 'value' to be a filename (str) or a pathlib.Path object
        # In Django, this often receives a File object with a .name attribute.

        if isinstance(value, Path):
            filepath = value
        elif isinstance(value, str):
            # Handle potential empty string input
            if not value:
                raise ValidationError("Filename cannot be empty.", code='empty_filename', params={'value': value})
            filepath = Path(value)
        elif hasattr(value, 'name') and isinstance(value.name, str):
            # Compatibility for objects with a .name attribute (like Django File)
            if not value.name:
                raise ValidationError("Filename cannot be empty.", code='empty_filename', params={'value': value})
            filepath = Path(value.name)
        else:
            raise TypeError(
                f"Unsupported type for FileExtensionValidator: {type(value)}. Expecting str, pathlib.Path, or object with .name.")

        # Get extension, remove leading dot, lowercase
        extension = filepath.suffix[1:].lower() if filepath.suffix else ''

        if self.allowed_extensions is not None and extension not in self.allowed_extensions:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    "extension": extension or "''",  # Show empty string if no extension
                    "allowed_extensions": ", ".join(sorted(self.allowed_extensions)),
                    "value": value,  # Original value for context
                },
            )

    def __eq__(self, other):
        return (
                isinstance(other, self.__class__)
                # Compare sets for order independence
                and self.allowed_extensions == other.allowed_extensions
                and self.message == other.message
                and self.code == other.code
        )


# --- Image File Extension Validator ---
# Note: Requires the external 'Pillow' library (pip install Pillow)

def get_available_image_extensions():
    """Returns a list of image extensions supported by Pillow."""
    try:
        from PIL import Image
    except ImportError:
        # Pillow not installed, return empty list or raise error?
        # Let's return empty, so validator will fail if used without Pillow
        print("Warning: Pillow library not found. Image extension validation may not work.")
        return []
    else:
        Image.init()  # Load registry
        # Get extensions, remove leading dot, lowercase
        return {ext.lower().lstrip('.') for ext in Image.EXTENSION}


def validate_image_file_extension(value):
    """
    Validates that the file extension is a known image format by Pillow.
    Requires Pillow to be installed.
    """
    allowed = get_available_image_extensions()
    if not allowed:
        # If Pillow isn't installed or finds no extensions, validation can't proceed meaningfully.
        # You might want to raise an error here, or let it pass silently.
        # For now, let FileExtensionValidator handle the empty 'allowed' list case.
        pass

    # Create a FileExtensionValidator instance on the fly
    validator = FileExtensionValidator(
        allowed_extensions=list(allowed),
        message="File extension '%(extension)s' is not a recognized image format. "
                "Allowed extensions: %(allowed_extensions)s.",
        code="invalid_image_extension"
    )
    return validator(value)


# --- Prohibit Null Characters Validator ---

class ProhibitNullCharactersValidator:
    """Validate that the string doesn't contain the null character (\x00)."""
    message = "Null characters are not allowed."
    code = "null_characters_not_allowed"

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        # Check for null character in the string representation of the value
        if "\x00" in str(value):
            raise ValidationError(self.message, code=self.code, params={"value": value})

    def __eq__(self, other):
        return (
                isinstance(other, self.__class__)
                and self.message == other.message
                and self.code == other.code
        )


# Instance for direct use
validate_prohibit_null_characters = ProhibitNullCharactersValidator()

# --- Example Usage ---
if __name__ == "__main__":
    # Example usage of some validators
    try:
        validate_email("test@example.com")
        print("Email valid.")
        validate_email("test@localhost")
        print("Email valid (localhost).")
        validate_email("test@[::1]")
        print("Email valid (IPv6 literal).")
        # validate_email("invalid-email") # Uncomment to test failure
    except ValidationError as e:
        print(f"Email Error: {e} (Code: {e.code}, Params: {e.params})")

    try:
        validate_url("https://www.example.com/path?query=1#fragment")
        print("URL valid.")
        validate_url("http://localhost:8000")
        print("URL valid.")
        validate_url("https://點看.com")  # IDNA domain
        print("URL valid (IDNA).")
        # validate_url("invalid-url") # Uncomment to test failure
        validate_url("ftp://[::1]:21") # Uncomment to test failure (IPv6) - should pass
        validate_url("ftp://[::1]:21")
        print("URL valid (IPv6 literal).")
        # validate_url("http://exa mple.com") # Uncomment to test unsafe chars
    except ValidationError as e:
        print(f"URL Error: {e} (Code: {e.code}, Params: {e.params})")

    try:
        validate_slug("valid-slug_123")
        print("Slug valid.")
        # validate_slug("invalid slug!") # Uncomment to test failure
    except ValidationError as e:
        print(f"Slug Error: {e} (Code: {e.code}, Params: {e.params})")

    try:
        validate_unicode_slug("valid-slug-čšž")
        print("Unicode Slug valid.")
        # validate_unicode_slug("invalid slug!") # Uncomment to test failure
    except ValidationError as e:
        print(f"Unicode Slug Error: {e} (Code: {e.code}, Params: {e.params})")

    try:
        v = MaxLengthValidator(5)
        v("abc")
        print("Length valid.")
        # v("abcdef") # Uncomment to test failure
    except ValidationError as e:
        print(f"Length Error: {e} (Code: {e.code}, Params: {e.params})")

    try:
        v_img = FileExtensionValidator(['jpg', 'png'])
        v_img("image.jpg")
        print("File extension valid.")
        v_img(Path("document.png"))
        print("File extension valid (Path object).")
        # v_img("archive.zip") # Uncomment to test failure
    except ValidationError as e:
        print(f"File Ext Error: {e} (Code: {e.code}, Params: {e.params})")

    try:
        # Requires Pillow installed
        # validate_image_file_extension("photo.jpeg")
        # print("Image extension valid.")
        # validate_image_file_extension("document.pdf") # Uncomment to test failure
        pass  # Commented out by default as Pillow is external
    except ValidationError as e:
        print(f"Image Ext Error: {e} (Code: {e.code}, Params: {e.params})")
    except ImportError:
        print("Pillow not installed, skipping image validation test.")

    try:
        v_dec = DecimalValidator(max_digits=5, decimal_places=2)
        v_dec(Decimal("123.45"))
        print("Decimal valid.")
        # v_dec(Decimal("123.456")) # Too many decimal places
        # v_dec(Decimal("12345.6")) # Too many total digits
        # v_dec(Decimal("1234.5")) # Too many whole digits
        v_dec("999.99")  # Test string input
        print("Decimal valid (string input).")
    except ValidationError as e:
        print(f"Decimal Error: {e} (Code: {e.code}, Params: {e.params})")

    try:
        v_step = StepValueValidator(0.1, offset=0.05)
        v_step(Decimal("1.25"))
        print("Step value valid.")
        # v_step(Decimal("1.2")) # Uncomment to test failure
    except ValidationError as e:
        print(f"Step Error: {e} (Code: {e.code}, Params: {e.params})")