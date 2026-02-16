#!/usr/bin/env python3
"""
Build script for Kizuna Platform
Minifies CSS and JavaScript for production
"""

import os
import re


def minify_css(css_content):
    """Basic CSS minification."""
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # Remove whitespace
    css_content = re.sub(r'\s+', ' ', css_content)
    # Remove spaces around special characters
    css_content = re.sub(r'\s*([{};:,>+~])\s*', r'\1', css_content)
    # Remove trailing semicolons before closing braces
    css_content = re.sub(r';}', '}', css_content)
    return css_content.strip()


def minify_js(js_content):
    """Basic JavaScript minification."""
    # Remove single-line comments (but not URLs)
    js_content = re.sub(r'(?<!:)//.*$', '', js_content, flags=re.MULTILINE)
    # Remove multi-line comments
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
    # Remove excessive whitespace (basic)
    js_content = re.sub(r'\n\s*\n', '\n', js_content)
    return js_content.strip()


def build():
    """Build static assets for production."""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    # Minify CSS
    css_file = os.path.join(static_dir, 'css', 'style.css')
    css_min_file = os.path.join(static_dir, 'css', 'style.min.css')
    
    if os.path.exists(css_file):
        with open(css_file, 'r') as f:
            css_content = f.read()
        
        minified_css = minify_css(css_content)
        
        with open(css_min_file, 'w') as f:
            f.write(minified_css)
        
        print(f"CSS minified: {len(css_content)} -> {len(minified_css)} bytes ({100 - len(minified_css)/len(css_content)*100:.1f}% reduction)")
    
    # Minify JavaScript
    js_file = os.path.join(static_dir, 'js', 'main.js')
    js_min_file = os.path.join(static_dir, 'js', 'main.min.js')
    
    if os.path.exists(js_file):
        with open(js_file, 'r') as f:
            js_content = f.read()
        
        minified_js = minify_js(js_content)
        
        with open(js_min_file, 'w') as f:
            f.write(minified_js)
        
        print(f"JS minified: {len(js_content)} -> {len(minified_js)} bytes ({100 - len(minified_js)/len(js_content)*100:.1f}% reduction)")
    
    print("Build complete!")


if __name__ == '__main__':
    build()
