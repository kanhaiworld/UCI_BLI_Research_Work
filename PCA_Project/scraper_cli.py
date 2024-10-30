import argparse 
import os 

from data_scraper import (
    split_images, 
    scrape_with_selenium, 
    scrape_all_before_after, 
    scrape_all_general, 
    generate_outlines
)

def main():
    parser = argparse.ArgumentParser(
        description="Data Scraper CLI for web scraping and image processing."
    )

    subparsers = parser.add_subparsers(dest="command", help="Choose a command to run")

     # Split Images
    split_parser = subparsers.add_parser("split_images", help="Split images into before/after")
    split_parser.add_argument("input_folder", type=str, help="Folder with input images")
    split_parser.add_argument("output_folder", type=str, help="Folder to save split images")

    # Scrape with Selenium
    selenium_parser = subparsers.add_parser("scrape_with_selenium", help="Scrape images from a URL using Selenium")
    selenium_parser.add_argument("output_folder", type=str, help="Folder to save scraped images")
    selenium_parser.add_argument("--url", type=str, default="https://galleryofcosmeticsurgery.com/gallery-category/dr-sadati/nose/female-rhinoplasty/",
                                 help="URL to scrape (optional)")

    # Scrape All Before After
    before_after_parser = subparsers.add_parser("scrape_all_before_after", help="Scrape before/after images")
    before_after_parser.add_argument("max_pics", type=int, help="Maximum number of pictures to scrape")
    before_after_parser.add_argument("page_indx", type=int, help="Starting page index")
    before_after_parser.add_argument("before", type=str, help="Folder to save 'before' images")
    before_after_parser.add_argument("after", type=str, help="Folder to save 'after' images")
    before_after_parser.add_argument("--url", type=str, default="https://www.plasticsurgery.org/photo-gallery/procedure/rhinoplasty/page/",
                                     help="Base URL for scraping (optional)")

    # Scrape All General
    general_parser = subparsers.add_parser("scrape_all_general", help="Scrape general images")
    general_parser.add_argument("max_pics", type=int, help="Maximum number of pictures to scrape")
    general_parser.add_argument("page_indx", type=int, help="Starting page index")
    general_parser.add_argument("folder", type=str, help="Folder to save scraped images")
    general_parser.add_argument("--url", type=str, default="https://www.plasticsurgery.org/photo-gallery/procedure/rhinoplasty/page/",
                                help="Base URL for scraping (optional)")

    # Generate Outlines
    outline_parser = subparsers.add_parser("generate_outlines", help="Generate outlines for images")
    outline_parser.add_argument("save_folder", type=str, help="Folder to save outlines")
    outline_parser.add_argument("images", type=str, help="Folder with images for outline generation")

    args = parser.parse_args()

    if args.command == "split_images":
        split_images(args.input_folder, args.output_folder)
    elif args.command == "scrape_with_selenium":
        scrape_with_selenium(args.output_folder, args.url)
    elif args.command == "scrape_all_before_after":
        scrape_all_before_after(args.max_pics, args.page_indx, args.before, args.after, args.url)
    elif args.command == "scrape_all_general":
        scrape_all_general(args.max_pics, args.page_indx, args.folder, args.url)
    elif args.command == "generate_outlines":
        generate_outlines(args.save_folder, args.images)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()