from common.file_management.file_manager import FileManager

if __name__ == "__main__":
    # Test the FileManager class with different app names
    user_manager = FileManager("user_app")
    content_manager = FileManager("content_app")
    analytics_manager = FileManager("analytics_app")

    # Test writing and reading text files
    user_manager.write('temp', 'user_list.txt', 'Alice\nBob\nCharlie')
    content = user_manager.read('temp', 'user_list.txt', file_type='text')
    print("User list content:", content)

    # Test writing and reading JSON files
    json_data = {'title': 'Latest Article', 'author': 'Jane Doe', 'tags': ['tech', 'ai', 'ml']}
    content_manager.write('data', 'article_metadata.json', json_data, file_type='json')
    json_content = content_manager.read('data', 'article_metadata.json', file_type='json')
    print("Article metadata:", json_content)

    # Test writing and reading HTML files
    html_content = '<html><body><h1>Monthly Report</h1><p>This is the analytics report for June 2023.</p></body></html>'
    analytics_manager.write('temp', 'monthly_report.html', html_content, file_type='html')
    html_read = analytics_manager.read('temp', 'monthly_report.html', file_type='html')
    print("Monthly report content:", html_read)

    # Test file existence
    print("user_list.txt exists:", user_manager.file_exists('temp', 'user_list.txt'))
    print("nonexistent.txt exists:", content_manager.file_exists('temp', 'nonexistent.txt'))

    # Test listing files
    print("Files in analytics temp directory:", analytics_manager.list_files('temp'))

    # Test deleting files
    user_manager.delete_file('temp', 'user_list.txt')
    print("After deletion, user_list.txt exists:", user_manager.file_exists('temp', 'user_list.txt'))

    # Test writing without cleaning
    content_manager.write('temp', 'raw_content.txt', 'This is uncleaned content with special characters: – — " "', clean=False)
    uncleaned_content = content_manager.read('temp', 'raw_content.txt', file_type='text')
    print("Uncleaned content:", uncleaned_content)

    # Test JSON specific methods
    json_handler = content_manager.json_handler
    print("JSON keys:", json_handler.get_keys('data', 'article_metadata.json'))
    print("JSON values:", json_handler.get_values('data', 'article_metadata.json'))
    print("JSON items:", json_handler.get_items('data', 'article_metadata.json'))


    # Test HTML specific methods
    html_handler = analytics_manager.html_handler
    links = html_handler.extract_links('temp', 'monthly_report.html')
    print("Extracted links from report:", links)
    extracted_text = html_handler.extract_text('temp', 'monthly_report.html')
    print("Extracted text from report:", extracted_text)

    # Clean up test files
    analytics_manager.delete_file('temp', 'monthly_report.html')
    content_manager.delete_file('temp', 'raw_content.txt')
    content_manager.delete_file('data', 'article_metadata.json')

    print("All tests completed.")
