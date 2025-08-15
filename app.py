import os
import logging
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from urllib.parse import urlparse
import tempfile
import re
from web_scraper import get_website_text_content
from pdf_generator import generate_pdf

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

def is_valid_url(url):
    """Validate and sanitize URL"""
    try:
        # Add http:// if no scheme is provided
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        
        # Check if URL has valid scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            return False, None
            
        # Block potentially dangerous schemes
        if parsed.scheme not in ['http', 'https']:
            return False, None
            
        # Block local/private addresses
        if parsed.netloc.lower() in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False, None
            
        return True, url
    except Exception:
        return False, None

def clean_filename(title):
    """Generate a clean filename from page title"""
    if not title:
        return "scraped_content"
    
    # Remove or replace invalid filename characters
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = re.sub(r'\s+', '_', title.strip())
    
    # Limit length
    if len(title) > 100:
        title = title[:100]
    
    return title or "scraped_content"

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_content():
    """Scrape website content and generate PDF"""
    try:
        url = request.form.get('url', '').strip()
        
        if not url:
            flash('Please enter a URL', 'error')
            return redirect(url_for('index'))
        
        # Validate URL
        is_valid, cleaned_url = is_valid_url(url)
        if not is_valid:
            flash('Please enter a valid URL', 'error')
            return redirect(url_for('index'))
        
        app.logger.info(f"Scraping content from: {cleaned_url}")
        
        # Extract content using trafilatura
        try:
            content = get_website_text_content(str(cleaned_url))
            if not content or len(content.strip()) < 10:
                flash('No content could be extracted from this URL. The page might be empty or protected.', 'error')
                return redirect(url_for('index'))
        except Exception as e:
            app.logger.error(f"Error extracting content: {str(e)}")
            flash('Failed to extract content from the website. Please try a different URL.', 'error')
            return redirect(url_for('index'))
        
        # Extract title from content (first line is usually the title)
        lines = content.split('\n')
        title = None
        for line in lines:
            if line.strip():
                title = line.strip()
                break
        
        if not title:
            title = "Scraped Content"
        
        # Generate PDF
        try:
            pdf_buffer = generate_pdf(title, content, cleaned_url)
            
            # Create a temporary file for download
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.write(pdf_buffer.getvalue())
            temp_file.close()
            
            filename = f"{clean_filename(title)}.pdf"
            
            app.logger.info(f"PDF generated successfully: {filename}")
            
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
            
        except Exception as e:
            app.logger.error(f"Error generating PDF: {str(e)}")
            flash('Failed to generate PDF document. Please try again.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        app.logger.error(f"Unexpected error in scrape_content: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API endpoint for AJAX scraping"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip() if data else request.form.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL
        is_valid, cleaned_url = is_valid_url(url)
        if not is_valid:
            return jsonify({'error': 'Invalid URL provided'}), 400
        
        # Extract content
        try:
            content = get_website_text_content(str(cleaned_url))
            if not content or len(content.strip()) < 10:
                return jsonify({'error': 'No content could be extracted from this URL'}), 400
        except Exception as e:
            app.logger.error(f"Error extracting content: {str(e)}")
            return jsonify({'error': 'Failed to extract content from the website'}), 400
        
        # Extract title
        lines = content.split('\n')
        title = None
        for line in lines:
            if line.strip():
                title = line.strip()
                break
        
        if not title:
            title = "Scraped Content"
        
        return jsonify({
            'success': True,
            'title': title,
            'content_length': len(content),
            'url': cleaned_url
        })
        
    except Exception as e:
        app.logger.error(f"Error in API scrape: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
