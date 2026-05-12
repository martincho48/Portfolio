#import the libraries
import joblib
import matplotlib.pyplot as plt
import os


def prediction():

    #Define the path for reading the model

    script_dir = os.path.dirname(__file__)
    file_name = 'sarima.pkl'
    path_merged = os.path.join(script_dir, file_name)
    print(f'path is: \n{path_merged}')

    #Load the model from disk
    loaded_model = joblib.load(path_merged)

    #Define interactive inputs:
    while True:  
        start_date = input("Enter START date=number (1968-04 = 0):")

        #check if string is numeric
        if start_date.isnumeric():
            #convert string into integer
            start_date=int(start_date)

            end_date= input("Enter END date=number:")
            
            #check if string is numeric
            if end_date.isnumeric():
                #convert string into integer
                end_date=int(end_date)

                #check if end is longer than start
                if end_date>start_date:
                    break
                else:
                    print('START date must be longer that END date!!!')
            else:
                print('Input must be integer!!!')
        else:
            print('Input must be integer!!!')

    #Fit the model before prediction (You have to do it if you use Arima models)
    model_fit = loaded_model.fit()

    #Predict
    predict = model_fit.predict(start=start_date, end=end_date)

    print(f'predicted data: \n{predict}')

    print(f'Congrats - all went OK :-)')

if __name__ == '__main__':
    prediction()
