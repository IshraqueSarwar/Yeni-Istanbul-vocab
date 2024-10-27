import pytesseract
import cv2
from deep_translator import GoogleTranslator
from tqdm import tqdm
import pickle
import os
import random
from gtts import gTTS
from playsound import playsound
import time
import glob, os
from fpdf import FPDF

# settings
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract"
abs_data_path = os.path.abspath("data/")




def txt_to_pdf(txt_file, pdf_file):
    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Add a font that supports Turkish characters
    pdf.add_font("DejaVu", "", "data/fonts/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    # Open the .txt file with UTF-8 encoding and add content to the PDF
    with open(txt_file, "r", encoding="utf-8") as file:
        for line in file:
            pdf.cell(0, 10, txt=line.strip(), ln=True)

    # Save the PDF file
    pdf.output(pdf_file)




def get_swap_dict(d):
    return {v: k for k, v in d.items()}

def convert_to_turk_char(input_word):
	converted_word = ""
	for i in range(len(input_word)):
		if(input_word[i]=="i"):
			converted_word+="i"
		elif(input_word[i]=="2"):
			converted_word+="ç"
		elif(input_word[i]=="3"):
			converted_word+="ğ"
		elif(input_word[i]=="0"):
			converted_word+="ö"
		elif(input_word[i]=="5"):
			converted_word+="ş"
		elif(input_word[i]=="4"):
			converted_word+="ü"
		else:
			converted_word+=input_word[i]

	return converted_word

def test(file_name, option=1):
	#option 1 is turkish - english
	#option 2 is english -turkish
	#option 3 is turkish voice to text

	with open("data/"+file_name+".pickle", "rb") as handle:
		sozluk = pickle.load(handle)


	wrong = []
	count = 1
	total_words = len(sozluk)



	print_banner()

	num_of_words_to_test = -2
	while(not -2<num_of_words_to_test<total_words+1):
		num_of_words_to_test =int(input(f"Number of words you want to practice. Total words for this unit: {total_words} (type -1 for full test)\n>"))

	if(num_of_words_to_test==-1):
		num_of_words_to_test=total_words
	else:
		total_words = num_of_words_to_test



	if option==1:
		
		q_words = [str(i) for i in sozluk.keys()]

		while(num_of_words_to_test):
			qs = q_words[random.randint(0, len(q_words)-1)]
			
			user_input = input(f"{count}/{total_words}. {qs}: ").lower().strip(' ')
			if(user_input!=sozluk[qs]):
				wrong.append(qs)
			
			q_words.remove(qs)
			# print(q_words)
			count+=1
			num_of_words_to_test-=1
	
	elif option==2:
		sozluk = get_swap_dict(sozluk)
		q_words = [str(i) for i in sozluk.keys()]

		while(num_of_words_to_test):
			qs = q_words[random.randint(0, len(q_words)-1)]
			
			user_input = input(f"{count}/{total_words}. {qs} (special characters: İ=i, Ç=2, Ğ=3, Ö=0, Ş=5, Ü=4)\n{count}/{total_words}>").lower().strip(' ')
			# converting the special chars
			user_input = convert_to_turk_char(user_input)
			print(f"""|-->{user_input}\n""")

			if(user_input!=sozluk[qs]):
				wrong.append(qs)
			
			q_words.remove(qs)
			# print(q_words)
			count+=1
			num_of_words_to_test-=1
	else:
		
		q_words = [str(i) for i in sozluk.keys()]
		
		repeat = False
		qs = ""

		while(num_of_words_to_test):

			if(not repeat):
				qs = q_words[random.randint(0, len(q_words)-1)]
			

			path = f"{abs_data_path}\\voice\\{sozluk[qs]}.mp3"
			gTTS(text=qs, lang = "tr").save(path)
			time.sleep(1)
			playsound(path)
			os.remove(path)
			
			user_input = input(f"Listen... Enter T to relisten... (special characters: İ=i, Ç=2, Ğ=3, Ö=0, Ş=5, Ü=4)\n{count}/{total_words}>").lower().strip(' ')
			# converting the special chars
			user_input = convert_to_turk_char(user_input)
			print(f"""|-->{user_input}\n""")

			if(user_input!="t"):
				if(user_input!=qs):
					wrong.append(qs)
				
				q_words.remove(qs)
				# print(q_words)
				count+=1

				repeat = False
				num_of_words_to_test-=1
			else:
				repeat = True


			




	os.system("cls")

	acc = round( ( (total_words-len(wrong)) /total_words*100), 2)
	print(f"RESULT: You made {len(wrong)} mistakes. Accuracy = {acc}%\nMistakes:\n")
	for i in wrong:
		print(f"{i} : {sozluk[i]}")
	print("\n\n")

	input("press <Enter> to return...")





# for now only adds data from images
def add_words(file_name, final_file):
	dict_tr_en = get_translation(file_name)

	

	if os.path.exists("data/"+final_file+".pickle"):
		print("file exists, adding and compiling to existing...")
		with open("data/"+final_file+".pickle", "rb") as handle:
			temp = pickle.load(handle)

		dict_tr_en.update(temp)



		# remove the old file
		os.remove("data/"+final_file+".pickle")

		with open("data/"+final_file+".pickle", "wb") as handle:
			pickle.dump(dict_tr_en, handle, protocol=pickle.HIGHEST_PROTOCOL)

	else:
		print("file doesn't exist, compiling new file...")
		with open("data/"+final_file+".pickle", "wb") as handle:
			pickle.dump(dict_tr_en, handle, protocol=pickle.HIGHEST_PROTOCOL)


	# remove
	print(dict_tr_en)
	print(len(dict_tr_en))


def get_translation(file_name):
	text = pytesseract.image_to_string(cv2.imread(file_name), lang="tur")
	text = text.replace("\n", ", ").split(", ")
	
	word_list = []
	for w in text:
		if(w!=''):
			w = w.replace(".","").lower()
			word_list.append(w)
	

	translated_dict_en_tr = translate(word_list)
	
	return translated_dict_en_tr




def translate(word_list):
	sozluk = {}
	for word in tqdm(word_list):
		word = word.replace(",","")
		
		translated_word = GoogleTranslator(source='auto', target='en').translate(word).lower()
		
		if word not in sozluk:
			sozluk[word] = translated_word
	
	return sozluk


def print_desc():
	BEIGE='\33[36m'
	PURPLE = '\033[0;35m' 
	CYAN = "\033[36m"
	LIGHT_VIOLET ='\33[95m'
	
	desc = f"""{LIGHT_VIOLET}This is a free software. For the listening test and\nadding more vocab to the dictionary, you'll need internet connection\n{CYAN}"""
	print(desc)

def print_banner():
	os.system("cls")
	BEIGE='\33[36m'
	PURPLE = '\033[0;35m' 
	CYAN = "\033[36m"


	banner = f"""
	{PURPLE}
 __   __         _   _     _              _           _                        _     
 \ \ / /__ _ __ (_) (_)___| |_ __ _ _ __ | |__  _   _| | __   _____   ___ __ _| |__  
  \ V / _ \ '_ \| | | / __| __/ _` | '_ \| '_ \| | | | | \ \ / / _ \ / __/ _` | '_ \ 
   | |  __/ | | | | | \__ \ || (_| | | | | |_) | |_| | |  \ V / (_) | (_| (_| | |_) |
   |_|\___|_| |_|_| |_|___/\__\__,_|_| |_|_.__/ \__,_|_|   \_/ \___/ \___\__,_|_.__/ 
                                			by ishraque sarwar siam

 	{CYAN}
	"""

	print(banner)



def get_level_unit():
	print_banner()
	print("Which level and unit do you want to practice?")

	os.chdir("data/")
	list_of_files = glob.glob("*.pickle")
	count = 1
	for index, file in enumerate(list_of_files):
	    print(f"{index+1}. {file}".replace(".pickle",""))
	print()
	user_input = input(">")

	os.chdir("../")
	return list_of_files[int(user_input)-1].replace(".pickle","")


def output_vocab_pdf(file_name):
	with open("data/"+file_name+".pickle", "rb") as handle:
		sozluk = pickle.load(handle)
	with open(f"{file_name}.txt", "w", encoding="utf-8") as f:
		for key in sozluk:
			f.write(f"{str(key)} --> {str(sozluk[key])}\n")

	txt_to_pdf(f"{file_name}.txt", f"{file_name}.pdf")

	os.remove(f"{file_name}.txt")

def menu():
	while(True):
		print_banner()
		print_desc()
		print("""1. Take Turkish to English test.\n2. Take English to Turkish test.\n3. Take listening test.\n4. Get vocab pdf.\n5. Add vocab.\n6. Exit""")

		user_input = ord(input("Enter option: "))-48

		if(0<user_input<7 or user_input == 65 or user_input==33):
			if(user_input == 65 or user_input == 33 or user_input==6):
				break
			else:
				if(user_input==1):
					file_user_selected = get_level_unit()
					test(file_user_selected)
					

				elif(user_input==2):
					file_user_selected = get_level_unit()
					test(file_user_selected,user_input)
					
					

				elif(user_input==3):
					file_user_selected = get_level_unit()
					test(file_user_selected,user_input)

				elif(user_input==4):
					file_user_selected = get_level_unit()
					output_vocab_pdf(file_user_selected)

				elif(user_input==5):
					user_input = input("Enter input png name: ")
					user_input_2 = input("Enter save file name: ")
					add_words(user_input, user_input_2)

				

				
					





if __name__ == "__main__":
	#for now we're hardcoding the fine name. Later if I feel mutlu enough I let the user do whatever the hell they want
	
	menu()

	# add_words("u6-3.png", "a1-6")

	