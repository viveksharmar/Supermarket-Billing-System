import mysql.connector 
import qrcode
import pandas
import tkinter as tk
from tkinter import ttk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image
import pyttsx3

initialize=pyttsx3.init()

# Connect to MySQL database
connect=mysql.connector.connect(host='localhost',user='root',password='Vivek@31#',database='mart')

# Checking connectivity of database
if connect.is_connected():
    print("Successful Connection to Database")
else:
    print("Not Connected to Database")

# Creation of cursor--Used to execute query/statements to communicate with MySQL
cursor=connect.cursor()

# Function to display stock

def display_stock():
    cursor.execute('Select * from product_details order by item_name' )
    products=cursor.fetchall()
    # for taking column names/headings using list comprehension
    # print(cursor.description) #List of Tuples(whose first element is column heading)
    columns=[desc[0] for desc in cursor.description]
    # print(columns)
    # creating dataframe for better look/display
    stock=pandas.DataFrame(products,columns=columns)
    print("Available Stock")
    initialize.say("Here's your Available Stock")
    initialize.runAndWait()
    print(stock)
    
# display_stock()




# Function to edit the quantity of product or stock

def edit_quantity():
    cursor.execute("Select item_name from product_details")
    # print(cursor.fetchall()) # List of Tuples(Having item name and null)-- Therefore List Comprehension
    items=[row[0] for row in cursor.fetchall()]
    # print(items)
    print("Enter the name of the product in dialog box and select whose quantity is to be changed:")
    
    def on_select(event):
        selected_item = listbox.get(listbox.curselection())  # Retrieve the selected item
        result_var.set(selected_item)
    
    def on_key_release(event):
        input_text = entry.get()
        filtered_items = [item for item in items if item.lower().startswith(input_text.lower())]
        listbox.delete(0, tk.END)
        for item in filtered_items:
            listbox.insert(tk.END, item)
        
    # Create a Tkinter window
    root = tk.Tk()
    root.title("Autocomplete Dropdown")

    # Create an entry field
    entry = ttk.Entry(root)
    entry.pack()

    # Create a listbox
    listbox = tk.Listbox(root)
    listbox.pack()

    # Create a result variable
    result_var = tk.StringVar()

    # Create a label to display the selected item
    result_label = ttk.Label(root, textvariable=result_var)
    result_label.pack()

    # Bind events
    entry.bind('<KeyRelease>', on_key_release)
    listbox.bind('<<ListboxSelect>>', on_select)

    root.mainloop()
    
    # Print the selected item as the output
    quantity_to_be_changed = result_var.get()
    print("You selected:", quantity_to_be_changed)
    
    new_quantity=int(input("Enter the updated or new quantity(in kg/packets):"))
    query=(f"update product_details set quantity_in_kg_or_packet={new_quantity} where item_name='{quantity_to_be_changed}'")
    cursor.execute(query)
    connect.commit()
    print("Quantity Updated Successfully!!")
    initialize.say("Quantity Updated Successfully")
    initialize.runAndWait()    
    
# edit_quantity()


# Function to generate bill
purchase={}
purchase['Items']=[]
purchase['Quantity']=[]
purchase['Price']=[]
sum=0


def generate_bill():
    cursor.execute("Select item_name from product_details")
    items=[row[0] for row in cursor.fetchall()]
    # print(items)
    print("Enter the name of the product in dialog box and select:")
    
    def on_select(event):
        selected_item = listbox.get(listbox.curselection())  # Retrieve the selected item
        result_var.set(selected_item)
    
    def on_key_release(event):
        input_text = entry.get()
        filtered_items = [item for item in items if item.lower().startswith(input_text.lower())]
        listbox.delete(0, tk.END)
        for item in filtered_items:
            listbox.insert(tk.END, item)
        
    # Create a Tkinter window
    root = tk.Tk()
    root.title("Autocomplete Dropdown")

    # Create an entry field
    entry = ttk.Entry(root)
    entry.pack()

    # Create a listbox
    listbox = tk.Listbox(root)
    listbox.pack()

    # Create a result variable
    result_var = tk.StringVar()

    # Create a label to display the selected item
    result_label = ttk.Label(root, textvariable=result_var)
    result_label.pack()

    # Bind events
    entry.bind('<KeyRelease>', on_key_release)
    listbox.bind('<<ListboxSelect>>', on_select)

    root.mainloop()
    
    # Print the selected item as the output
    bill_item = result_var.get()
    print("Item Name:", bill_item)
    item=bill_item
    
    if item!='':    
        quant=float(input("Quantity(in kgs or packets)="))
            
        cursor.execute(f"select price_per_kg_or_packet from product_details where item_name='{bill_item}'")
        pr=cursor.fetchone()[0]
        # print(pr)
        cursor.execute(f'update product_details set quantity_in_kg_or_packet=quantity_in_kg_or_packet-{quant} where item_name="{bill_item}"')
        connect.commit()
        price=quant*pr
        global sum
        sum=sum+price
        
        purchase['Items'].append(bill_item)
        purchase['Quantity'].append(quant)
        purchase['Price'].append(price)
        # print(purchase)
        # bill=pandas.DataFrame(purchase)
        # print(bill)
    else:
        return item

    


# Function to send to mail to customer

def mail():
    mail=MIMEMultipart()
    mail["From"]="viveksharma.it26@jecrc.ac.in"
    mail["To"]=f"{customer_email}"
    mail["Subject"] = "Thanking You for visiting our store!!"
    mail.attach(MIMEText(f"Greetings! Your total bill was {sum}. Have a nice day!!", "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("viveksharma.it26@jecrc.ac.in", "Vivek@31#")
        server.sendmail("viveksharma.it26@jecrc.ac.in", "viveksharmajpr21@icloud.com", mail.as_string())
        server.quit()
        print("Email sent successfully!")
        initialize.say("Confirmation email sent successfully")
        initialize.runAndWait()
    except Exception as e:
        print(f"An error occurred: {e}")   
     
 
 
    
# Function to get upi payments

def upi():
    # Define your UPI payment details
    upi_id = "9057657468@ybl"
    amount = sum
    note = "Payment for services"  # Optional note

    # Create the UPI payment link
    upi_link = f"upi://pay?pa={upi_id}&am={amount}&cu=INR&tn={note}"

    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_link)
    qr.make(fit=True)

    # Create a QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Display the QR code
    img.show() 
  

# Main-Menu

while True:
    print("Select Your Choice from 0-3 and Enter\n")
    print("Choices:\n 0=To exit or quit\n 1=Display List of Items with their Price and Stock\n 2=Edit the Stock\n 3=Generate Bill\n")

    choice=int(input('Enter the choice='))

    if choice==1:
        display_stock()
    elif choice==2:
        edit_quantity()
    elif choice==3:
        customer_email=input("Customer's Email=")
        while True:
            a=generate_bill()
            if a=='':
                break
        bill=pandas.DataFrame(purchase)
        print(bill)
        print(f'Total value={sum}')
        initialize.say(f'Total Bill is {sum} sir')
        initialize.runAndWait()
        
        mode=input("Mode of Payment(Cash/Upi)=")
        mode=mode.lower()
        if mode=='cash':
            print("Money Accepted, Thank You Sir")
            initialize.say("Money Accepted, Thank You Sir")
            initialize.runAndWait()
        elif mode=='upi':
            upi()
            print("Thank You Sir!")
        else:
            print("Invalid Mode of Payment")
        if customer_email!='':
            mail()
        else:
            print('No email given')
    elif choice==0:
        break   
    else:
        print('Invalid Choice given')     
        initialize.say('Please enter the correct choice sir')
        initialize.runAndWait()


# Close the cursor and database connection when done
cursor.close()
connect.close()
