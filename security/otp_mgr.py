"""
OTP Generation and QR Code Scanning Tool

This module provides functionality for:
- Reading QR codes from image files
- Extracting OTP secrets from scanned QR codes
- Generating time-based one-time passwords (TOTP) from shared secrets or URIs

Dependencies:
- `pyotp` for TOTP generation
- `pyzbar` for barcode/QR code decoding
- `Pillow` (PIL) for image handling

Example Usage:
    python otp_qr_tool.py

Typical Use Case:
This tool is useful when setting up 2FA via QR codes and you need to extract
the secret key or generate OTPs directly from images or encoded URIs.

"""

import pyotp
from pyzbar.pyzbar import decode
from PIL import Image


class GenerateOTP:
    def __init__(self):
        """Initialize the GenerateOTP utility class."""
        pass

    @staticmethod
    def generate_otp_from_secret(secret_key):
        """
        Generates and prints the current TOTP from a given secret key.

        Args:
            secret_key (str): Base32-encoded shared secret used for OTP generation.

        Example:
            generate_otp_from_secret("JBSWY3DPEHPK3PXP")
        """
        totp = pyotp.TOTP(secret_key)
        print(totp.now())  # Generates the current OTP

    @staticmethod
    def scan_codes(image_path):
        """
        Scans a QR or barcode image and extracts decoded string data.

        Args:
            image_path (str): File path to the QR or barcode image.

        Returns:
            list[tuple[str, str]]: List of (barcode_type, decoded_data) pairs if any codes found.
            None: If no codes are found or the image cannot be processed.
        """
        with open(image_path, 'rb') as image_file:
            image = Image.open(image_file)
            decoded_data = decode(image)

            if decoded_data:
                code_data = [(d.type, d.data.decode('utf-8')) for d in decoded_data]
                return code_data

        return None

    @staticmethod
    def generate_otp_from_image(image_path):
        """
        Scans a QR code from an image and prints the decoded content and generated OTP.

        Args:
            image_path (str): File path to the QR code image.

        Behavior:
            - Prints decoded QR code content.
            - Generates OTP if QR contains a valid otpauth:// URI.
            - Uses `generate_otp_from_uri()` internally.
        """
        with open(image_path, 'rb') as image_file:
            image = Image.open(image_file)
            decoded_data = decode(image)

            if decoded_data:
                code_data = [(d.type, d.data.decode('utf-8')) for d in decoded_data]

                print('Scanned Codes:')
                for barcode_type, barcode_data in code_data:
                    print('Barcode Type:', barcode_type)
                    print('Barcode Data:', barcode_data)

                otp = otp_generator.generate_otp_from_uri(code_data[0][1])
                if otp:
                    print('Generated OTP:', otp)
            else:
                print('No barcodes or QR codes found in the image.')

    @staticmethod
    def generate_otp_from_uri(uri):
        """
        Parses a full otpauth URI and generates a one-time password (OTP).

        Args:
            uri (str): A string of the form `otpauth://totp/...` typically encoded in QR codes.

        Returns:
            str: The current OTP if successful.
            None: If the URI cannot be parsed or OTP generation fails.

        Example:
            generate_otp_from_uri("otpauth://totp/Label?secret=ABCDEF123456&issuer=Example")
        """
        try:
            otp_data = pyotp.parse_uri(uri)
            return otp_data.now()
        except Exception as e:
            print(f"Error parsing OTP URI: {e}")
            return None


if __name__ == '__main__':
    otp_generator = GenerateOTP()
    img = './data/qr_code.png'  # Replace with your barcode/QR code image path

    data = otp_generator.scan_codes(image_path=img)
