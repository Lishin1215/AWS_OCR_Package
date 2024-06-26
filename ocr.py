# Detects text in a document stored in an S3 bucket. Display polygon box around text and angled text
# import boto3
# import io
# from PIL import Image, ImageDraw
#
#
# def process_text_detection(s3_connection, client, bucket, document):
#     # Get the document from S3
#     s3_object = s3_connection.Object(bucket, document)
#     s3_response = s3_object.get()
#
#     stream = io.BytesIO(s3_response['Body'].read())
#     image = Image.open(stream)
#
#     # To process using image bytes:
#     # image_binary = stream.getvalue()
#     # response = client.detect_document_text(Document={'Bytes': image_binary})
#
#     # Detect text in the document
#     # Process using S3 object
#     response = client.detect_document_text(
#         Document={'S3Object': {'Bucket': bucket, 'Name': document}})
#
#     # Get the text blocks
#     blocks = response['Blocks']
#     width, height = image.size
#     print('Detected Document Text')
#
#     # Create image showing bounding box/polygon the detected lines/text
#     for block in blocks:
#         # Display information about a block returned by text detection
#         print('Type: ' + block['BlockType'])
#         if block['BlockType'] != 'PAGE':
#             print('Detected: ' + block['Text'])
#             print('Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")
#
#         print('Id: {}'.format(block['Id']))
#         if 'Relationships' in block:
#             print('Relationships: {}'.format(block['Relationships']))
#         print('Bounding Box: {}'.format(block['Geometry']['BoundingBox']))
#         print('Polygon: {}'.format(block['Geometry']['Polygon']))
#         print()
#         draw = ImageDraw.Draw(image)
#         # Draw WORD - Green -  start of word, red - end of word
#         if block['BlockType'] == "WORD":
#             draw.line([(width * block['Geometry']['Polygon'][0]['X'],
#                         height * block['Geometry']['Polygon'][0]['Y']),
#                        (width * block['Geometry']['Polygon'][3]['X'],
#                         height * block['Geometry']['Polygon'][3]['Y'])], fill='green',
#                       width=2)
#
#             draw.line([(width * block['Geometry']['Polygon'][1]['X'],
#                         height * block['Geometry']['Polygon'][1]['Y']),
#                        (width * block['Geometry']['Polygon'][2]['X'],
#                         height * block['Geometry']['Polygon'][2]['Y'])],
#                       fill='red',
#                       width=2)
#
#             # Draw box around entire LINE
#         if block['BlockType'] == "LINE":
#             points = []
#
#             for polygon in block['Geometry']['Polygon']:
#                 points.append((width * polygon['X'], height * polygon['Y']))
#
#             draw.polygon((points), outline='black')
#
#             # Display the image
#     image.show()
#
#     return len(blocks)
#
#
# def main():
#     session = boto3.Session(profile_name='profile-name')
#     s3_connection = session.resource('s3')
#     client = session.client('textract', region_name='region')
#     bucket = ''
#     document = ''
#     block_count = process_text_detection(s3_connection, client, bucket, document)
#     print("Blocks detected: " + str(block_count))
#
#

from venv import logger
import boto3
import io



class ClientError:
    pass


class TextractWrapper:
    """Encapsulates Textract functions."""

    def __init__(self, textract_client, s3_resource, sqs_resource):
        """
        :param textract_client: A Boto3 Textract client.
        :param s3_resource: A Boto3 Amazon S3 resource.
        :param sqs_resource: A Boto3 Amazon SQS resource.
        """
        self.textract_client = textract_client
        self.s3_resource = s3_resource
        self.sqs_resource = sqs_resource


    def detect_file_text(self, *, document_file_name=None, document_bytes=None):
        """
        Detects text elements in a local image file or from in-memory byte data.
        The image must be in PNG or JPG format.

        :param document_file_name: The name of a document image file.
        :param document_bytes: In-memory byte data of a document image.
        :return: The response from Amazon Textract, including a list of blocks
                 that describe elements detected in the image.
        """
        if document_file_name is not None:
            with open('assests/Referral_letter_example.jpg', 'rb') as document_file:
                document_bytes = document_file.read()
        try:
            response = self.textract_client.detect_document_text(
                Document={"Bytes": document_bytes}
            )
            logger.info("Detected %s blocks.", len(response["Blocks"]))

            # Extract the text from the response
            result_string = ""
            for block in response['Blocks']:
                if block['BlockType'] in ['WORD', 'LINE']:
                    result_string += block['Text']
                    # result_string += block['Text'] + " "

                    if block['Text'].endswith('.'):
                        result_string += "\n"
                    else:
                        result_string += " "

            return result_string

        except ClientError:
            logger.exception("Couldn't detect text.")
            raise
        # else:
        #     return response


if __name__ == "__main__":
    session = boto3.Session()
    textract_client = session.client('textract')
    s3_resource = session.resource('s3')
    sqs_resource = session.resource('sqs')

    textract_wrapper = TextractWrapper(textract_client, s3_resource, sqs_resource)
    response = textract_wrapper.detect_file_text(document_file_name= 'assests/Referral_letter_example.jpg')
    print(response)