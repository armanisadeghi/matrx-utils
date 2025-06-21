
from PIL import Image, ImageEnhance
from pathlib import Path
from matrx_utils.file_handling.file_handler import FileHandler


class ImageHandler(FileHandler):
    def __init__(self, app_name, batch_print=False):
        super().__init__(app_name, batch_print=batch_print)

    # Custom Methods
    def custom_read_image(self, path):
        try:
            with Image.open(path) as img:
                self._print_link(path=path, message="Read Image file")
                return img.copy()

        except Exception as e:
            print(f"Error reading image from {path}: {str(e)}")
            self._print_link(path=path, message=f"READ IMAGE ERROR {str(e)}", color="red")
            return None

    def custom_write_image(self, path, image):
        try:
            self._ensure_directory(Path(path))
            image.save(path)
            self._print_link(path=path, message="Image File Saved")
            return True
        except Exception as e:
            self._print_link(path=path, message="Error saving Image", color="red")
            print(f"Error saving image to {path}: {str(e)}")
            return False

    def custom_append_image(self, path, image, position=(0, 0)):
        try:
            base_image = self.custom_read_image(path)
            if base_image:
                base_image.paste(image, position)
                return self.custom_write_image(path, base_image)
            return False
        except Exception as e:
            print(f"Error appending image to {path}: {str(e)}")
            return False

    def custom_delete_image(self, path):
        return self.delete(path)

    # Core Methods
    def read_image(self, root, path):
        full_path = self._get_full_path(root, path)
        return self.custom_read_image(full_path)

    def write_image(self, root, path, image):
        full_path = self._get_full_path(root, path)
        return self.custom_write_image(full_path, image)

    def append_image(self, root, path, image, position=(0, 0)):
        full_path = self._get_full_path(root, path)
        return self.custom_append_image(full_path, image, position)

    def delete_image(self, root, path):
        full_path = self._get_full_path(root, path)
        return self.custom_delete_image(full_path)

    # File Type-specific Methods
    def get_image_size(self, root, path):
        image = self.read_image(root, path)
        return image.size if image else None

    def get_image_format(self, root, path):
        image = self.read_image(root, path)
        return image.format if image else None

    def get_image_mode(self, root, path):
        image = self.read_image(root, path)
        return image.mode if image else None

    def resize_image(self, root, path, width, height):
        image = self.read_image(root, path)
        if image:
            resized_image = image.resize((width, height))
            return self.write_image(root, path, resized_image)
        return False

    def convert_image_format(self, root, path, target_format):
        image = self.read_image(root, path)
        if image:
            target_path = Path(path).with_suffix(f'.{target_format.lower()}')
            return self.write_image(root, target_path, image)
        return False

    def crop_image(self, root, path, left, top, right, bottom):
        image = self.read_image(root, path)
        if image:
            cropped_image = image.crop((left, top, right, bottom))
            return self.write_image(root, path, cropped_image)
        return False

    def rotate_image(self, root, path, angle):
        image = self.read_image(root, path)
        if image:
            rotated_image = image.rotate(angle)
            return self.write_image(root, path, rotated_image)
        return False

    def merge_images(self, root, path_list, output_path):
        images = [self.read_image(root, path) for path in path_list]
        if all(images):
            widths, heights = zip(*(i.size for i in images))
            total_width = sum(widths)
            max_height = max(heights)
            merged_image = Image.new('RGB', (total_width, max_height))
            x_offset = 0
            for img in images:
                merged_image.paste(img, (x_offset, 0))
                x_offset += img.width
            return self.write_image(root, output_path, merged_image)
        return False

    def add_watermark(self, root, path, watermark_path, position=(0, 0), opacity=128):
        image = self.read_image(root, path)
        watermark = self.read_image(root, watermark_path)
        if image and watermark:
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            alpha = watermark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity / 255.0)
            watermark.putalpha(alpha)
            image.paste(watermark, position, watermark)
            return self.write_image(root, path, image)
        return False

    def adjust_brightness(self, root, path, factor):
        image = self.read_image(root, path)
        if image:
            enhancer = ImageEnhance.Brightness(image)
            brightened_image = enhancer.enhance(factor)
            return self.write_image(root, path, brightened_image)
        return False

    def convert_to_grayscale(self, root, path):
        image = self.read_image(root, path)
        if image:
            grayscale_image = image.convert('L')
            return self.write_image(root, path, grayscale_image)
        return False

    def create_thumbnail(self, root, path, size):
        image = self.read_image(root, path)
        if image:
            image.thumbnail(size)
            return self.write_image(root, path, image)
        return False

    def flip_image(self, root, path, direction='horizontal'):
        image = self.read_image(root, path)
        if image:
            if direction == 'horizontal':
                flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
            elif direction == 'vertical':
                flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
            else:
                print(f"Invalid flip direction: {direction}. Use 'horizontal' or 'vertical'.")
                return False
            return self.write_image(root, path, flipped_image)
        return False
