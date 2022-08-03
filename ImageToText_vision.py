'''Extract text from image OCR using Google Vision API'''

import io
import os
from google.cloud import vision
import pandas as pd
import csv

class ReadImage():
    def __init__(self,img):
        self.img = img
    
    def vision_result(self):    
        credential_path = r"APIKey2.json"
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
        client = vision.ImageAnnotatorClient()

        with io.open(self.img, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content) 
        response = client.document_text_detection(image=image)
        result = response.text_annotations

        return result
    
    def text_to_tsv(self):
        df_list = []
        print('File_name is  ',self.img)

        result = self.vision_result()
        clean_text = []
        clean_text.append(result)

        clean_list = str(clean_text[0][0])
        filter_text = clean_list.split('\ndescription:')[1].split('bounding_poly {')[0].replace('\\n','\n').replace('"','').strip()

        data_list = []
        filter_list=filter_text.split('\n')

        data_list.append(self.img)
        shelf_data = self.img.split('Shelf')[-1].replace('.png','')
        shelf = shelf_data.split('_')[0].strip()
        prod_num = shelf_data.split('_')[-1]
        data_list.append(shelf)
        data_list.append(prod_num)

        upc_list = []
        if ' ' in filter_list[0] and (filter_list[0].split(' ')[0].isdigit()):
            upc_list.append(filter_list[0].split(' ')[0])
        else:
            if ' ' in filter_list[0] and filter_list[0].split(' ')[0].isalpha() and len(filter_list)>=2:
                upc_list.append(filter_list[1])
            else:
                upc_list.append(filter_list[0])

        if len(upc_list) == 1:
            if len(upc_list[0]) <5 and len(filter_list) >= 2:
                if len(filter_list) >= 3 and len(filter_list[1]) <= 5:
                    data_list.append(filter_list[2])
                else:
                    data_list.append(filter_list[1])
            else:
                data_list.append(upc_list[0])

            if len(filter_list)==1:
                prod_desc = filter_list[0].strip()
                if prod_desc:
                    data_list.append(prod_desc)
            else:
                if filter_list[1].strip().isdigit() and len(filter_list) >= 3:
                    if filter_list[2].strip().isdigit() and len(filter_list) >= 3:
                        prod_desc = filter_list[3].strip()
                        if prod_desc:
                            data_list.append(prod_desc)
                    else:
                        prod_desc = filter_list[2].strip()
                        if prod_desc:
                            data_list.append(prod_desc)

                else:
                    prod_desc = filter_list[1].strip()
                    if prod_desc:
                        data_list.append(prod_desc)

        df_list.append(data_list)

        print('DATA: ',data_list,' ======= ')

        df = pd.DataFrame(df_list,columns=['filename','Shelf','Product','UPC','Product_description'])
        df.to_csv('output.tsv',sep='\t', quoting=csv.QUOTE_NONE)
        print('\n')
        print('File successfully created')
    

if __name__ == '__main__':  
    root = ReadImage('page_3_Shelf 3_7.png')
    root.text_to_tsv()

