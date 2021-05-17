
#imports----------------------------------------------------------------------- IMPORTS
import sys

#user friendly exception tracebacks--------------------------------
import traceback



#-------------------------------------------------------------------------------------------------------------- 
#-------------------------------------------------------------------------------------------------------------- MAIN
#-------------------------------------------------------------------------------------------------------------- 
if __name__ == '__main__':


    #get user input (from command line)---------------------------------------- USER INPUT  
    num_inputs = len(sys.argv)

    if num_inputs < 2:
        print("Please use the following command line arguments: \n1.) path to query file \n2.) path to output file")
        print("Example: python " + sys.argv[0] + " query_list.txt results.txt")

    else: 
        query_path = sys.argv[1]
        output_file = sys.argv[2]

        #debug(verify input)
        print("Input 01: " + query_path + " Input 02: " + output_file)