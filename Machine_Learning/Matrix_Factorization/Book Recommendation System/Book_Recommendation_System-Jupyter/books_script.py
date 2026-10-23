#import the libraries
import joblib
import os


def prediction():

    #Define the path for reading the model
    script_dir = os.path.dirname(__file__) #path to the current script

    pivot_name = 'pivot_table_SVD.pkl'
    model_name = 'corr_matrix_SVD.pkl'

    path_merged_model = os.path.join(script_dir, model_name)
    path_merged_pivot = os.path.join(script_dir, pivot_name)

    #Load the model
    loaded_model = joblib.load(path_merged_model)
    loaded_pivot = joblib.load(path_merged_pivot)


    #get all the book titles in the pivot table columns
    title=loaded_pivot.index
   
    #convert it into a list
    title_list=list(title)

    #window with input parameter
    while True:  
        book_title_to_find = input("Enter the whole book title:")


        if book_title_to_find in loaded_pivot.index:
            index_location = loaded_pivot.index.get_loc(book_title_to_find)
            print(f"************ \nBook '{book_title_to_find}' was found!")

            #pass the index into a corr matrix
            corr_index=loaded_model[index_location]
    

            #filter the most similar books
            recommendation_list=list(title[(corr_index<1)&(corr_index>0.8)])
            print(f'************ \nRecommended Books: \n {recommendation_list}')

            break

        elif book_title_to_find =='q':
            break

        else:
            print(f"************ \n{book_title_to_find}' not found in the pivot table. Try again or press 'q' to quit.")
        
            #Print suggestions
            filtered_list = [item for item in title_list if book_title_to_find in item]
            print(f'************ \nTry similar items: \n{filtered_list}')

if __name__ == '__main__':
    prediction()


    
