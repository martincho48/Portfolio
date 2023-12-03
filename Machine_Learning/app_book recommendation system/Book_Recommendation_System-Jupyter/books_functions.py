import pandas as pd
import matplotlib.pyplot as plt


#create a function which split string in part and chooses the last part
def country_split(row):  
    row = row.split(',') #creates a list
    result=row[-1] #take the last item of the list
    return result


#bar chart for data in Series=1D array with index
def bar_chart( df, x_label, y_label):

    x_col=df.index
    y_col=df.values

    #plot
    df.plot(kind='bar', x=y_col, y=x_col, legend=False)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()




#horizontal bar chart function
def hor_col_chart( df, x_col, y_col, x_label, y_label):

    #choose the first 'values' authors
    #top_items=df.iloc[0:num_dis_val].sort_values(x_col, ascending=True)

    #plot
    df.plot(kind='barh', x=y_col, y=x_col, legend=False)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()


#horizontal bar chart function
def curve_chart( df, x_col, y_col, x_lim, y_lim, x_label, y_label):

    #plot
    df.plot( x=x_col, y=y_col, legend=False, marker='o')

    plt.xlim(0,x_lim)
    plt.ylim(0,y_lim)

    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.grid(True)
    plt.show()



#book index finder function
def book_index_finder(book_title, pivot_name):
    
    book_title_to_find = book_title

    #define title list
    title_list=list(pivot_name.index)

    if book_title_to_find in pivot_name.index:
        index_location = pivot_name.index.get_loc(book_title_to_find)
        print(f"The index of '{book_title_to_find}' is at location {index_location}.")
    
    
    else:
        print(f"'{book_title_to_find}' not found in the pivot table.")
        #Print suggestions
        suggestions = [item for item in title_list if book_title_to_find in item]
        print(f'Try similar items: \n{suggestions}')
        index_location=''
    
    return index_location
