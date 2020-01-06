#The solution run sin py 2.7

import json

#class holding function which are common to both task
class Common():
    
    #to take input through the file
    def file_input(self):
        file_name=raw_input("Enter the file name which contain the input-: ")
        file_read=open(file_name+".json")
        data=""
        with open(file_name+".json") as f:
            data=json.load(f)
        return data['questions']
    
    #to write the json data into the file
    def file_write(self,json_data):
        with open('data.json', 'w') as outfile:
            json.dump(json_data, outfile,indent=4,sort_keys=True)
     
    #show options to user if available     
    def show_options(self,ques):
        print ques['text'] 
        if 'options' in ques:
            for option in  ques['options']:
                print option      

    #to get the instruction using the format function
    def get_instruction(self,text,all_data):
        #print(text)
        try:
            if(text.get('instruction_var')):
                # print("ok")
                #print((tuple((all_data.get(j)) for j in text.get('instruction_var'))))
                # print(all_data)
                #print(text['instruction'])
                return text['instruction'] % ((tuple((all_data.get(j)) for j in text.get('instruction_var'))))
            return text['instruction']
        except Exception as e:
            return text['instruction']
    

class Bot(Common):
    
    def __init__(self,task=1):        

        #list of all possible keys in the given input file
        self.keywords=["questions","instruction","text","var","conditions",
                        "options","formula","calculated_variable","instruction_var",
                        "list_var","list_length"]

        #dictionary to store th value of variables add a extra variable because of wrong json data given
        self.variables={"row":[]}
        self.commonFunc=Common()
        self.questions=self.commonFunc.file_input()
        self.output={}
        self.task=task

    #function to execute the expressions     
    def execute_code(self,expression,local_ns):
        '''first compiled the code and then executing the code using exec function 
        we can directly call the exec function but it makes it slow.
        Took refernce from-: http://lucumr.pocoo.org/2011/2/1/exec-in-python/
        '''
        code = compile("answer="+expression, '<string>', 'exec')
        exec("answer="+expression,{},local_ns)
                
    #to produce the json output as required by task1 and task2
    def produce_output(self,time,message,options=None,isBot=True,isUser=False):
        if self.task==1:
            key_name='stage'+str(time)
            if key_name not in self.output:
                self.output[key_name]=dict()
                self.output[key_name]["Bot Says"]=list()
                self.output[key_name]["User Says"]=""
            if isBot:
                self.output[key_name]["Bot Says"].append({"message":{"text":message}})
                if options:
                    quick_reply=[]
                    for option in options:
                        quick_reply.append({"content_type":"text","title":option,"payload":option.lower()})                
                    self.output[key_name]["Bot Says"][-1]["message"]["quick_replies"]=quick_reply
            else:
                self.output[key_name]["User Says"]=message
        else:
            key_name='stage'+str(time)
            if isBot:
                if key_name not in self.output:
                    self.output[key_name]=list()
                self.output[key_name].append({"message":{"text":message}})
                if options:
                    quick_reply=[]
                    for option in options:
                        quick_reply.append({"content_type":"text","title":option,"payload":option.lower()})                
                    self.output[key_name][-1]["message"]["quick_replies"]=quick_reply
                
    #the main program
    def start_procedure(self):
        times=1    

        #iterating through all the objects of the key questions input json file 
        for i in self.questions:
            
            #if the object conatins instruction then print them
            if self.keywords[1] in i:

                #if the instruction has list_var key the run a loop till list_length and print the instruction
                if i.get(self.keywords[9])=="True":
                    for j in range(0,int(i.get(self.keywords[10]))):
                        local=self.variables
                        local.update({"i+1":j+1,"i":j,"str(t_matrix[i])":self.variables['t_matrix'][j]})
                        message=self.commonFunc.get_instruction(i,local)
                        print(message)
                        self.produce_output(time=times,message=message)

                # if it don't have any list_var variable then simply print the instruction
                else:
                    message=self.commonFunc.get_instruction(i,self.variables)
                    print(message)
                    self.produce_output(time=times,message=message)
            
            #if objects contain calculated_variable then save the variable using the given formula           
            elif self.keywords[7] in i:
                local_ns=self.variables
                local_ns[i[self.keywords[3]]]=""
                local_ns.update({"answer":""})
                self.execute_code(i["formula"],local_ns)
                self.variables[i[self.keywords[3]]]=local_ns['answer']
            
            #if the objects contain conditions then check the conditions and perform the action accordingly    
            elif self.keywords[4] in i:
                check=""
                for condition in  i.get(self.keywords[4]):
                    for j in condition:
                        check=check+j
                age=self.variables.get('age')
                local_ns={"check":check,"age":age,"answer":True}
                self.execute_code(check,local_ns)
                message=i.get(self.keywords[2])
                while local_ns['answer']!=False:
                    self.produce_output(time=times,message=message)            
                    user_input=raw_input(message)
                    self.produce_output(time=times,message=user_input,isBot=False)
                    local_ns["age"]=user_input
                    age=self.variables.get('age')
                    self.execute_code(check,local_ns)
                    times=times+1

            #if the object has text and var then take input from the user and assign it to the given variable                                                                              
            elif self.keywords[2] in i:
                message=i.get(self.keywords[2])
                if self.keywords[5] in i:
                    self.produce_output(time=times,message=message,options=i[self.keywords[5]])            
                else:
                    self.produce_output(time=times,message=message)                                
                self.commonFunc.show_options(i)
                user_input=""
                while user_input=="":
                    user_input=raw_input()
                if '[' in i.get(self.keywords[3]):
                    variable_name=i.get(self.keywords[3])
                    start=variable_name.find('[')
                    self.variables[variable_name[0:start]].append([])
                    self.variables[variable_name[0:start]][int(variable_name[start+1:-1])]=user_input

                    #extra part because of wrong json data given as indicated in the image
                    try:
                        self.variables['row'].append([])
                        self.variables['row'][int(variable_name[start+1:-1])]=user_input
                    except:
                        pass

                else:                                   
                    self.variables[i.get(self.keywords[3])]=user_input
                self.produce_output(time=times,message=user_input,isBot=False)
                times=times+1

        #write the generated json data into a file    
        self.commonFunc.file_write(self.output)

if __name__=="__main__":                                                    
    k=Bot()
    k.start_procedure()
