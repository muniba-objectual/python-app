#!/usr/bin/env python

import argparse
import sys
import csv
import os

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def main(client, customer_id, directory):
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
          campaign.id,
          campaign.name
        FROM campaign
        ORDER BY campaign.id"""

    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create the path for the CSV file
    csv_file_path = os.path.join(directory, 'campaigns.csv')

    # Open a CSV file for writing
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        
        # Write the header row to the CSV file
        writer.writerow(['Campaign ID', 'Campaign Name'])
        
        # Issues a search request using streaming.
        stream = ga_service.search_stream(customer_id=customer_id, query=query)

        for batch in stream:
            for row in batch.results:
                # Write campaign data to the CSV file
                writer.writerow([row.campaign.id, row.campaign.name])

if __name__ == "__main__":
    # Default values
    default_customer_id = '3265367567'
    default_directory = './campaigns'

    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    googleads_client = GoogleAdsClient.load_from_storage()

    parser = argparse.ArgumentParser(
        description="Lists all campaigns for specified customer."
    )
    # The following argument(s) should be provided to run the example.
    parser.add_argument(
        "-c",
        "--customer_id",
        type=str,
        default=default_customer_id,
        help=f"The Google Ads customer ID (default: {default_customer_id}).",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=default_directory,
        help=f"Directory to save the CSV file (default: {default_directory}).",
    )
    args = parser.parse_args()

    try:
        main(googleads_client, args.customer_id, args.directory)
    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)