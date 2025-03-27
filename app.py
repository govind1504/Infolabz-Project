import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
import plotly.express as px
import pickle


data = pd.read_csv("Social_Media.csv")
Registered_user_file = "Registeration.csv"

#create a file if not exist 
if not os.path.exists(Registered_user_file):
    df = pd.DataFrame(columns = ('Name' , 'Email','Username' , 'Password'))
    df.to_csv(Registered_user_file,index=False)
else:
    df = pd.read_csv(Registered_user_file,dtype={'Name':str,'Email':str,'Username':str,'Password':str})

df['Email'] = df['Email'].str.strip()
df['Name'] = df['Name'].str.strip()
df['Username'] = df['Username'].str.strip()
df['Password'] = df['Password'].str.strip()

#if code is running for the first time we have to assign authenticated False and none User_id
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# State of Session 
query_params = st.query_params
if 'auth' in query_params and query_params['auth'] == 'True':
    st.session_state.authenticated = True
    st.session_state.user_id = query_params.get('user' , '')

with st.sidebar:
    if st.session_state.authenticated: #if session is already stared then this Sidebar
    
        selected = option_menu(f"welcome / {st.session_state.user_id} 👋" , ['Analysis' , 'Data' ,'Comparision','Boston House Price','Logout'] ,menu_icon=['house'], icons=['bar-chart','database',"clipboard2-pulse-fill",'robot','box-arrow-right'],default_index=0 )
    else:   #otherwise this
        
        selected = option_menu("Register/Login" , ['Login' , 'Register'] ,menu_icon=['house'], icons=['lock','pen'],default_index=0 )
    
# Login 
if selected == 'Login':
    st.title("Login")
    with st.form("Login",enter_to_submit=True):
        username = st.text_input("Username").strip()
        Password = st.text_input("Enter Password" , type='password').strip()
        Reg_submit = st.form_submit_button("Login",icon=":material/login:")
        if Reg_submit :
            if username in df['Username'].values:
                User_data = df.loc[df['Username'] == username]
                if Password in User_data['Password'].values:
                    #Session created just after login
                    st.session_state.authenticated = True
                    st.session_state.user_id = username
                    st.query_params.update(auth='True',user = username)
                    st.success('Login Successfully')
                    st.rerun()


                else:
                    st.error("Wrong Password")
            else:
                st.error("Username not found") 

#Register   
if selected == 'Register':
    st.title("Register")
    with st.form("Register"):
        
        name = st.text_input("Enter Name").strip()
        email = st.text_input("E-mail Address").strip()
        Username = st.text_input("Username").strip()
        Password = st.text_input("Password", type="password").strip()
        submit = st.form_submit_button("Register", icon=":material/app_registration:")

        if submit:
            if name and email and Username and Password:
                if email in df['Email'].values or Username in df['Username'].values:
                    if email in df['Email'].values:
                        st.error('Email Already Exists')
                    else:
                        st.error("Username Already Exists")
                else:
                    new_entry = pd.DataFrame({
                        'Name': [name],
                        "Email": [email],
                        "Username": [Username],
                        "Password": [Password]
                    })
                    df = pd.concat([df, new_entry], ignore_index=True)
                    df.to_csv(Registered_user_file, index=False)
                    st.success("Registration Successful! ")
            else:
                st.error("Please enter all the required details.")
#Analysis
if selected == "Analysis":
    st.title("Analysis 📊")
    popover = st.popover("Filter Platform")
    if popover:
        Instagram = popover.checkbox("Instagram" , True)
        Facebook = popover.checkbox("Facebook", True)
        Snapchat= popover.checkbox("Snapchat", True)
        Twitter=popover.checkbox("Twitter", True)
        Telegram = popover.checkbox("Telegram", True)
        LinkedIn = popover.checkbox("LinkedIn",True)
        Whatsapp = popover.checkbox("Whatsapp",True)

    #Function to show analysis of selected Platform

    def Selected(Platform):
            st.subheader(Platform)

            # Data
            
            pt = data[data['Platform'].isin([Platform])]
           

            # Age Vs Count

            col1 , col2  = st.columns(2)
            age_count = pt['Age'].value_counts().reset_index()
            age_count.columns = ['Age', 'Count']
            fig = px.bar(age_count, x='Age', y='Count', title=f'Age vs Count for {Platform} Users')
            col1.plotly_chart(fig)

            # Gender Distribution Pie Chart

            fig = px.pie(pt , names="Gender", title="Gender Distribution")
            st.plotly_chart(fig)
    
            # Usage according Gender
    
            Usage = pt.groupby('Gender')["Daily_Usage_Time (minutes)"].mean().reset_index()
            fig = px.bar(Usage , x="Gender" , y = "Daily_Usage_Time (minutes)" , title="Avg Usage Time By Gender")
            col2.plotly_chart(fig)

            # Comparision of Gender Posts by Age

            posts = pt.groupby("Age",as_index=False)['Posts_Per_Day'].mean()
            posts = pd.DataFrame(posts)
            
            fig = px.bar(posts , x = "Age" , y = "Posts_Per_Day" , barmode='group' , title="Avg Post Uploadation by different Age Group")
            st.plotly_chart(fig)
#Filter
    if Instagram:
        Selected("Instagram")
    if Facebook:
        Selected("Facebook")   
    if Snapchat:
        Selected("Snapchat")
    if Twitter:
        Selected("Twitter")
    if Telegram:
        Selected("Telegram")
    if LinkedIn:
        Selected("LinkedIn")
    if Whatsapp:
        Selected("Whatsapp")

#Data

if selected == 'Data':
    st.title("Data")
    st.subheader("Search Platform")
    Query = st.text_input("search").strip().lower()
    if Query:
        search_df =data[data['Platform'].str.lower().str.contains(Query)]
        search_data = search_df.to_csv()
        st.download_button('Export Data' , search_data , f"data.csv" , 'txt/csv')
        st.write(search_df)

#Compoarision
        
if selected == 'Comparision':
    st.title("Compare")
    col1 , col2 , col3 = st.columns([4,1,4],vertical_alignment='bottom',gap='large')
    platform1 = col1.selectbox("Select Platform 1",data['Platform'].unique())
    col2.write("## vs" )
    platform2 = col3.selectbox("Select Platform 2",data['Platform'].unique())
    if platform1 is not platform2:
        compare_df = data[data['Platform'].isin([platform1,platform2])]
        User_count = compare_df.groupby('Platform',as_index=False)['User_ID'].count()
        User_count = pd.DataFrame(User_count)
        fig = px.pie(User_count, names='Platform', values='User_ID' , title= 'Platform User Comparision')
        st.plotly_chart(fig)
        post_per_day_dist = compare_df.groupby('Platform' , as_index= False)['Posts_Per_Day'].value_counts()
        post_per_day_dist = pd.DataFrame(post_per_day_dist)

        # Post_per_day Distribution

        col1 , col2 = st.columns(2)
        
        fig = px.histogram(post_per_day_dist[post_per_day_dist['Platform'].isin([platform1])],x='Posts_Per_Day' , y = 'count',nbins=10 )
        col1.plotly_chart(fig)
        col1.write(platform1)
        fig = px.histogram(post_per_day_dist[post_per_day_dist['Platform'].isin([platform2])],x='Posts_Per_Day' , y = 'count',nbins=10 )
        col2.plotly_chart(fig)
        col2.write(platform2)
    else:
        st.warning("both platform should be different to compare")

model = pickle.load(open("Linear-model.pkl" , 'rb'))
def predict(dict):
    df = pd.DataFrame([dict])
    Pred = model.predict(df)
    return Pred[0]

# Boston House Price Prediction Model 
if selected == 'Boston House Price':
    st.title("Linear Model 🤖 ")
    st.subheader(':rainbow[Its House Prediction model based on multiple Features]')
    with st.form("Predict Boston House "):
        crim = st.slider("Crime Rate(%) " ,0 , 100 , 30)
        zn = st.slider (" proportion of residential land zoned for lots over 25,000 sq.ft." , 0 , 100 , 10)
        indus = st.slider("proportion of non-retail business acres per town." , 0 , 30 , 5)
        chas = st.selectbox("Near Charles River ?",("Yes" , "No"))
        chas = 1 if chas == "Yes" else 0
        Nox = st.slider("nitric oxides concentration (parts per 10 million)" , 0.0 , 1.0 ,0.3)
        rm = st.slider("Avg no of rooms per dwelling " , 0 , 8 , 1)
        Age = st.slider("Age(Years)" , 0,100 ,2)
        dict = {"CRIM":crim , "ZN" : zn , 'INDUS':indus , "CHAS":chas ,"NOX":Nox,"RM":rm,   "AGE" :Age, "DIS":3.79 , "RAD":9.54 , 'TAX' :408 ,'PTRATIO':18.45 , 'B' : 356.67, 'LSTAT' :12.65 }
        Predict = st.form_submit_button("Predict")
        if Predict:
            prediction = predict(dict)
            st.success(f"🏡 Predicted House Price: $ {prediction[0]*1000}")


 

# Logout
if selected == "Logout":
    st.title("Logout")
    st.write("Are you sure you want to logout?")
    
    if st.button("Yes, Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.query_params.clear()
        st.success("Logged out successfully")
        st.rerun()
    