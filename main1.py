from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from test import download_file,delete_file
import os
from icalendar import Calendar
from datetime import datetime, timedelta
import difflib

help_text = """
*Comment utiliser le bot :*

1. *Démarrage :*  
   Utilisez la commande `"/start [nom ou prénom ou les deux]"` pour lancer le bot. 
   Remplacez `[nom ou prénom]` par votre nom ou prénom.  
   *Note :* Si plusieurs utilisateurs ont le même prénom, vous devrez ajouter le nom pour permettre au bot de vous identifier correctement.

2. *Choix du jour :*  
   Le bot vous proposera de choisir un jour parmi la semaine courante pour obtenir l'emploi du temps du jour sélectionné.

   *Important :*
   - Si nous sommes *samedi* ou *dimanche*, le bot vous proposera les jours de la semaine *suivante*.

3. *Affichage de l'emploi du temps :*  
   Une fois que vous avez sélectionné un jour, le bot affichera l'emploi du temps correspondant à ce jour.

---

*Exemples :*
- "/start Ait el amiri"
- "/start Ait el amiri Amine"
 
---

"""

# Dictionary with names and corresponding numbers
correspondence_dict = {
    'Adelaide Gabriel': 6113,
    'Ait El Amiri Amine': 6961,
    'Ait Louhou Salah_Eddine': 5740,
    "Ait M'hand Mohamed_Yassine": 6986,
    'Andre Yanis': 5682,
    'Badra Mohamed': 6717,
    'Ben Amor Eya': 6713,
    'Benzakri Meryem': 6774,
    'Boudy Pierre': 6067,
    'Boussenna Mohamed_Amine': 6535,
    'Bouvier Robin': 6635,
    'Cazaux Aymeric': 6521,
    'Chahma Nael': 1835,
    'Croisant Anaelle': 3898,
    'Daouakha Sofien': 6728,
    'De Chivre Adrien Diop Karim': 6104,
    'Djelali Yanis': 6690,
    'Dumitrescu--Palcau Nicolas': 3877,
    'El Baz Yassine': 6832,
    'El Gholabzouri Abdelaziz': 5393,
    'Elmasrar Amine': 5769,
    'Ferreira Thomas': 6479,
    'Garchery Ethan': 5922,
    'Garnaud Dimitri': 6484,
    'Gastrin Nathan': 5475,
    'Ghezal Mattis': 5516,
    'Heddoun Reda': 4546,
    'Husser Antoine': 6473,
    'Kara Mehmed-Zaid': 6437,
    'Kollen Matthieu': 6909,
    'Le Strat Maxime': 6747,
    'Lignel Pierre': 6594,
    'Mati Merwan': 5449,
    'Maureille Jean': 747,
    'Meleiro Gabriel': 6871,
    'Ndiaye Ibrahima': 2846,
    'Ouezghari Assia': 4473,
    'Pendanx Leho': 6526,
    'Reggoug Aymane': 6797,
    'Regnault Thomas': 6259,
    'Renault Thomas': 5935,
    'Rigal Nathan': 4623,
    'Saadi Mehdi': 5609,
    'Samih Iliess': 6309,
    'Sancho Ugo': 6042,
    'Stite Amr': 6255,
    'Suisse De Sainte Claire Hugo': 912,
    'Traversino Eoghan': 6755,
    'Trepant Thomas': 6374,
    'Tribak Noussayba': 3873,
    'Vaudois Maxime': 6679,
    'Vlas lulian': 3769,
    'Zaguer Halima': 6420,
    'Zakri Yasser': 6448,
    'Zimmermann Jule': 6575
}

# Function to get the closest matching name
def get_closest_match(name):
    # Get all names from the dictionary
    all_names = list(correspondence_dict.keys())
    # Find the closest match
    closest_match = difflib.get_close_matches(name, all_names, n=1, cutoff=0.5)  # Adjust cutoff for stricter matching
    if closest_match:
        return closest_match[0], correspondence_dict[closest_match[0]]
    else:
        return None, "No close match found"


# Helper function to get the current week's start date
def get_week_start_date() -> datetime:
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    # Check if today is Saturday or Sunday
    if today.weekday() in [5, 6]:  # 5 is Saturday, 6 is Sunday
        start_of_week += timedelta(weeks=1)
    return start_of_week

# Helper function to get the date for a given day of the week
def get_date_for_day(start_date: datetime, day_name: str) -> datetime:
    day_map = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6,
    }
    day_delta = day_map.get(day_name)
    if day_delta is not None:
        return start_date + timedelta(days=day_delta)
    return None

def analyze_ics_file(file_path):
    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        return

    with open(file_path, 'rb') as file:
        cal = Calendar.from_ical(file.read())

        event_details_list = []

        for component in cal.walk():
            if component.name == "VEVENT":
                # Extracting event details
                subject = component.get('summary')
                start_time = component.get('dtstart').dt
                end_time = component.get('dtend').dt
                location = component.get('location')
                description = component.get('description')
                # Adding two hours to start and end time
                start_time_plus_two_hours = start_time + timedelta(hours=2) if isinstance(start_time, datetime) else start_time
                end_time_plus_two_hours = end_time + timedelta(hours=2) if isinstance(end_time, datetime) else end_time
                start_time_formatted = start_time_plus_two_hours.strftime('%H:%M') if isinstance(start_time, datetime) else start_time
                end_time_formatted = end_time_plus_two_hours.strftime('%H:%M') if isinstance(end_time, datetime) else end_time
                # Store details in a dictionary
                event_details = {
                    "subject": subject,
                    "start_time": start_time_formatted,
                    "end_time": end_time_formatted,
                    "location": location,
                    "description": description
                }

                event_details_list.append(event_details)

        # Separate variables to store details
        subjects = []
        start_times = []
        end_times = []
        locations = []
        descriptions = []

        for event in event_details_list:
            subjects.append(event['subject'])
            start_times.append(event['start_time'])
            end_times.append(event['end_time'])
            locations.append(event['location'])
            descriptions.append(event['description'])

        # Combine the collected data into a list of tuples for sorting
        events_for_sorting = list(zip(subjects, start_times, end_times, locations, descriptions))

        # Sort events by start time
        events_for_sorting.sort(key=lambda x: x[1])  # Sorting by start time (second element)


    return events_for_sorting

user_input = "default"
# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get user input if there are arguments
    user_input = ' '.join(context.args) if context.args else None

    # Store the user input in context.user_data
    if user_input:
        context.user_data['user_input'] = user_input
    # Define the inline keyboard options
    keyboard = [
        [InlineKeyboardButton("Comment ca marche", callback_data='ccm')],
        [InlineKeyboardButton("Emploi du temps", callback_data='edt')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a message with the inline keyboard
    await update.message.reply_text('Choisir une option: ', reply_markup=reply_markup)

async def ccm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text(help_text,parse_mode='Markdown')


# Function to handle button clicks
async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    command = query.data

    # Acknowledge the button click
    await query.answer()

    if command == 'ccm':
        await query.message.reply_text(help_text ,parse_mode='Markdown')

    elif command == 'edt':
        # Define the days of the week inline keyboard
        keyboard = [
            [InlineKeyboardButton("Lundi", callback_data='Monday')],
            [InlineKeyboardButton("Mardi", callback_data='Tuesday')],
            [InlineKeyboardButton("Mercredi", callback_data='Wednesday')],
            [InlineKeyboardButton("Jeudi", callback_data='Thursday')],
            [InlineKeyboardButton("Vendredi", callback_data='Friday')],
            [InlineKeyboardButton("Samedi", callback_data='Saturday')],
            [InlineKeyboardButton("Dimanche", callback_data='Sunday')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send a message with the days of the week inline keyboard
        await query.message.reply_text('Select a day of the week:', reply_markup=reply_markup)

    elif command in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        # Calculate the date for the selected day
        start_date = get_week_start_date()
        selected_date = get_date_for_day(start_date, command)
        if selected_date:
            name_input = context.user_data.get('user_input')
            closest_name, number = get_closest_match(name_input)
            await query.message.reply_text("Tu es "+closest_name + ".")
            formatted_date = selected_date.strftime("%Y-%m-%d")
            url = 'https://adeapp.bordeaux-inp.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources='+ str(number) +'&projectId=1&calType=ical&firstDate='+ formatted_date +'&lastDate='+ formatted_date +'&displayConfigId=71'
            print(url)
            local_filename = 'file.ics'  # Replace with your desired local filename
            download_file(url, local_filename)
            events =analyze_ics_file(local_filename)

            delete_file(local_filename)
            for event in events:
                subject, start_time, end_time, location, description = event
                await query.message.reply_text(
                    f"<b>Cours:</b> {subject}\n"
                    f"<b>Début du cours:</b> {start_time}\n"
                    f"<b>Fin du cours:</b> {end_time}\n"
                    f"<b>Lieu:</b> {location}",
                    parse_mode='HTML'
                )

        else:
            await query.message.reply_text('Invalid day selected.')

    else:
        await query.message.reply_text('Unknown command.')


app = ApplicationBuilder().token("7481193839:AAFU3UVmzaesvNjLgocb8LkXaqCVM7W5370").build()

app.add_handler(CommandHandler("ccm", ccm))
#app.add_handler(CommandHandler("edt", edt))

# Add command handler for the /start command
app.add_handler(CommandHandler("start", start))

# Add callback query handler for button clicks
app.add_handler(CallbackQueryHandler(handle_button_click))

app.run_polling()