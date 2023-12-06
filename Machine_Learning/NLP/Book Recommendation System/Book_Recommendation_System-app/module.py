import joblib
import os
import pandas as pd


class BookRecommendation:
    def __init__(self):
        script_dir = os.path.dirname(__file__)

        self.pivot_name = 'models/pivot_mine.pkl'
        self.model_urls = 'models/urls.pkl'

        self.path_merged_pivot = os.path.join(script_dir, self.pivot_name)
        self.path_merged_urls = os.path.join(script_dir, self.model_urls)

        self.loaded_pivot = joblib.load(self.path_merged_pivot)
        self.loaded_urls = joblib.load(self.path_merged_urls)


    def predict(self, book_title_to_find):

        #get all the book titles in the pivot table columns
        title=self.loaded_pivot.index

        if book_title_to_find in self.loaded_pivot.index:
            index_location = self.loaded_pivot.index.get_loc(book_title_to_find)

            #choose the searched book=row => columns with those who rated same book
            searched_book=self.loaded_pivot.iloc[index_location, :]

            #convert Series into dataframe
            same_book_readers=pd.DataFrame({'rating':searched_book})

            #keep just those who rated > 8, those who liked the book
            same_book_readers=same_book_readers.query('rating >= 8').reset_index()

            #convert a df into a list
            columns_to_keep=same_book_readers['best users'].tolist()

            #filter the columns
            filtered_pivot_table = self.loaded_pivot[columns_to_keep]

            #sum the rows
            score=filtered_pivot_table.sum(axis=1)

            #create df
            df = pd.DataFrame({'score':score}).sort_values('score', ascending=False)

            #slice first 10 best titles                   
            df=df[0:10]

            df = df.drop(columns=['score'])
            
            #merge dataframes
            df=df.merge(self.loaded_urls, on='title')
            df = df.rename(columns={df.columns[1]: 'Picture',
                                    df.columns[2]: 'Author',
                                    df.columns[0]: 'Title'
                                    })
            
            #change order of columns
            df=df[['Title', 'Author', 'Picture']]


            message1='Book title was found :-)'
            message2='Recommended Books:'



        else:
            recommendation = [item for item in list(title) if book_title_to_find in item]

            #compose dataframe
            df=pd.DataFrame({'title':recommendation})

            #merge dataframes
            df=df.merge(self.loaded_urls, on='title')
            df = df.rename(columns={df.columns[1]: 'Picture',
                                    df.columns[2]: 'Author',
                                    df.columns[0]: 'Title'
                                    })

            #change order of columns
            df=df[['Title', 'Author', 'Picture']]


            message1='Book title was NOT found :-('
            message2='Try to paste these book titles:'

        return df, message1, message2
    


""" #debug reason
recommendation = BookRecommendation()

df, message1, message2 = recommendation.predict('It') 

print('done') """