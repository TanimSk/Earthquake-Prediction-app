from kivymd.uix.button import MDFillRoundFlatIconButton, MDFillRoundFlatButton, MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.list import OneLineIconListItem as ListItem
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField
from kivymd_extensions.akivymd.uix.datepicker import AKDatePicker
from kivymd.uix.list import MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.core.audio import SoundLoader
from kivy.uix.image import Image
from kivy.utils import platform

from datetime import datetime
from jnius import autoclass
from pytz import timezone
# import webbrowser
import csv

SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.tanimsk.earthquake_predictor',
    servicename=u'Notify'
)

BASIC_RULES = '''[color=#2a2a2a]1. This app only shows the prediction of the highest earthquake of any date of the year 2022 but it is impossible to say where the earthquake will occure. 
The earthquake can occure in any place of the world.

2. If a prediction of any date becomes incorrect and a big earthquake occures than their will be a possibility of bigger 
earthquakes in the next 4 to 5 days.[/color]'''

GENERAL_TIPS = '''[color=#2a2a2a]1.Drop down; take cover under a desk or table and hold on.

2.Stay indoors until the shaking stops and you’re sure it’s safe to exit.

3.Stay away from bookcases or furniture that can fall on you.

4.Stay away from windows. In a high-rise building, expect the fire alarms and sprinklers to go off during a quake.

5.If you are in bed, hold on and stay there, protecting your head with a pillow.[/color]'''

BEFORE_EQ = '''[color=#2a2a2a]1.Learn how to survive during the ground motion. This is described in the “During the Earthquake” section below. 
The earthquake safety tips there will prepare you for the fast action needed – most earthquakes are over in 
seconds so knowing what to do instinctively is very important.

2.Teach all members of your family about earthquake safety. This includes:
the actions you should take, when an earthquake occurs, the safe places in a room such as under a strong desk, along interior walls, 
and places to avoid such as near windows, large mirrors, hanging objects, heavy furniture and fireplaces.[/color]'''

DURING_EQ = '''[color=#2a2a2a]1.If you are indoors, stay there. Quickly move to a safe location in the room such as under a strong desk, a strong table, or along an interior wall. The goal is to protect yourself from falling objects and be located near the structural strong points of the room. Avoid taking cover near windows, large mirrors, hanging objects, heavy furniture, heavy appliances or fireplaces.

2.If you are cooking, turn off the stove and take cover.

3.If you are outdoors, move to an open area where falling objects are unlikely to strike you. Move away from buildings, powerlines and trees.[/color]'''

AFTER_EQ = '''[color=#2a2a2a]1.Check for injuries, attend to injuries if needed, help ensure the safety of people around you.

2.Check for damage. If your building is badly damaged you should leave it until it has been inspected by a safety professional.

3.If you smell or hear a gas leak, get everyone outside and open windows and doors. If you can do it safely, turn off the gas 
at the meter. Report the leak to the gas company and fire department. Do not use any electrical appliances because a tiny spark could ignite the gas.[/color]'''

INFO = \
    '''[color=#2a2a2a]The predictions have been made by depending on a hypothesis (reference 1). This app is a part of that research. After one year the accuracy of the predictions will be shown and new predictions of the next year will be uploaded. We have taken the information of the previous  earthquakes form the website of USGS (reference 2).

Reference:
[color=#0645ad]
https://www.arcjournals.org/pdfs/ijarps/v6-i3/6.pdf/

https://earthquake.usgs.gov/

https://solarsystem.nasa.gov/ [/color]
[size=12sp]
Developer : [ref=https://tanimsk.github.io/Tanim-Sk][color=#0645ad]tanimsk.github.io/Tanim-Sk[/color][/ref]
Research : [ref=https://tanimsk.github.io/Tanim-Sk][color=#0645ad]mdsalmanmahmud.com[/color][/ref][/size]'''


class MainApp(MDApp):
    sm = None
    screen_main = None
    screen_query = None
    screen_settings = None
    screen_tips = None
    screen_country_selection = None

    selected_date = None
    minor_rating_label = None
    severe_rating_label = None
    sound = None

    btn_color = (149 / 255, 57 / 255, 106 / 255, 1)

    store = JsonStore('data.json')

    def on_start(self):
        self.sound = SoundLoader.load('./assets/click.wav')

        if platform == 'android':
            self.request_android_permissions()

    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            if not all([res for res in results]):
                self.request_android_permissions()

        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.FOREGROUND_SERVICE,
                             Permission.READ_EXTERNAL_STORAGE], callback)

    # ----------- WEB BROWSER ---------------
    # def load_url(self):
    #     print("printef")
    #     webbrowser.open("google.com")

    # ----------- Android Services ------------

    def start_service(self):

        if platform == 'android':
            service = autoclass(SERVICE_NAME)

            self.mActivity = autoclass(
                u'org.kivy.android.PythonActivity').mActivity
            argument = ''
            service.start(self.mActivity, argument)
            self.service = service

    def stop_service(self):
        if self.service:
            if platform == "android":
                self.service.stop(self.mActivity)
            self.service = None

    # ----------- Main Screen ------------

    def main_screen(self):
        self.screen_main = Screen(name="main_scrn")

        anouncement = \
            "The Earthquake of the highest magnitude\nof 2022 can be occured between January\nto February or April to August"

        label_year = MDLabel(
            text="Year 2022", font_style="H4",
            pos_hint={"y": .42}, halign="center"
        )

        date_label = MDLabel(
            text=datetime.now().strftime("%b %d, %y %a"),
            pos_hint={"y": .38}, halign="center"
        )

        graph_img = Image(
            source="./assets/Graph.png", pos_hint={"center_y": .64, "center_x": .5}, size_hint=(.85, .85)
        )

        label_anouncement = MDLabel(
            text=anouncement, pos_hint={"center_y": .38, "center_x": .5},
            halign="center", size=(100, 0)
        )

        search_btn = MDFillRoundFlatButton(
            text="Check Earthquake Possibility\nBy Date",
            pos_hint={"center_x": .5, "center_y": .25}, md_bg_color=self.btn_color,
            on_release=lambda *args: self.sm.switch_to(
                self.screen_query, direction='left'),
            on_press=self.click_sound
        )

        tips_btn = MDFillRoundFlatButton(
            text="TIPS", pos_hint={"center_x": .2, "center_y": .08}, md_bg_color=self.btn_color,
            on_release=lambda *args: self.sm.switch_to(
                self.screen_tips, direction='left'),
            on_press=self.click_sound
        )

        settings_btn = MDFillRoundFlatButton(
            text="SETTINGS", pos_hint={"center_x": .78, "center_y": .08}, md_bg_color=self.btn_color,
            on_release=lambda *args: self.sm.switch_to(
                self.screen_settings, direction='left'),
            on_press=self.click_sound
        )

        self.screen_main.add_widget(graph_img)
        self.screen_main.add_widget(date_label)
        self.screen_main.add_widget(label_year)
        self.screen_main.add_widget(label_anouncement)
        self.screen_main.add_widget(search_btn)
        self.screen_main.add_widget(tips_btn)
        self.screen_main.add_widget(settings_btn)

    # ------------- Query Screen -------------

    def date_selected(self, value):

        data_frame = csv.reader(
            open('./files/records.csv', "r"), delimiter=",")

        if value:

            Day = str(int(value.strftime('%d')) - self.store.get('data')['Time'])

            new_date = f"{value.strftime('%Y-%m')}-{Day.zfill(2)}"

            value = value.strftime("%Y-%m-%d")

            for row in data_frame:
                if new_date == row[0]:
                    minor_ratings = row[1]
                    severe_ratings = row[2]
                    break

        else:
            value = "Wrong Date Selected"

        minor_ratings = ""
        severe_ratings = ""

        self.selected_date.text = f"[size=15sp]Date Selected[/size]\n[size=25sp]{value}[/size]"

        if minor_ratings != "":
            self.minor_rating_label.text = f"[size=15sp]In this date, the highest\nEarthquake can be of magnitude:[/size]\n\n[size=35sp]{minor_ratings}[/size]"
        else:
            self.minor_rating_label.text = "[size=25sp]\nNot Found[/size]"

        if severe_ratings != "":
            self.severe_rating_label.text = f"[size=15sp] Less then 10% chance [/size]\n {severe_ratings} "
        else:
            self.severe_rating_label.text = ""

    date_picker = None

    def open_picker(self, *kwargs):
        date = datetime.now()

        self.date_picker._day_title = date.strftime("%d")
        self.date_picker._month_title = date.strftime("%B")
        self.date_picker._year_title = date.strftime("%Y")

        self.date_picker.open()

    def query_screen(self):
        self.screen_query = Screen(name="query_scrn")

        self.date_picker = AKDatePicker(
            callback=self.date_selected, year_range=(2022, 2032)
        )

        screen_name = MDLabel(
            text="Query", font_style="H4",
            pos_hint={"y": .40}, halign="center"
        )

        dialog_info = MDDialog(  # INFO
            title="Info",
            text=INFO,
            width_offset='10dp'
        )

        dialog_rules = MDDialog(  # RULES
            title="Basic Rules",
            text=BASIC_RULES,
            width_offset='10dp'
        )

        info_btn = MDIconButton(
            icon="information", pos_hint={"y": 0.75, "center_x": 0.2},
            # icon_size="50sp",
            # theme_icon_color='Custom', 
            # icon_color=self.btn_color,
            on_release=dialog_info.open,
            on_press=self.click_sound
        )

        rules_btn = MDIconButton(
            icon="book-open", pos_hint={"y": 0.75, "center_x": 0.8},
            # icon_size="50sp",
            # theme_icon_color='Custom', 
            # icon_color=self.btn_color,
            on_release=dialog_rules.open,
            on_press=self.click_sound
        )

        date_en_btn = MDFillRoundFlatIconButton(
            text=" Select Date  ", pos_hint={"center_x": .5, "center_y": .2}, icon="calendar-month-outline",
            md_bg_color=self.btn_color, on_release=self.open_picker, on_press=self.click_sound
        )

        self.selected_date = MDLabel(
            text="\n\n\n\n\nPlease Select Date", font_style="H4", markup=True,
            pos_hint={"center_y": .7}, halign="center"
        )
        self.minor_rating_label = MDLabel(
            text="", markup=True,
            pos_hint={"center_y": .52}, halign="center"
        )
        self.severe_rating_label = MDLabel(
            text="", markup=True, font_style="H4",
            pos_hint={"center_y": .36}, halign="center"
        )

        back_btn = MDIconButton(
            icon="arrow-left-drop-circle", pos_hint={"y": 0, "x": 0},
            # icon_size="50sp",
            on_release=lambda *args: self.sm.switch_to(
                self.screen_main, direction='right'),
            on_press=self.click_sound
        )

        self.screen_query.add_widget(info_btn)
        self.screen_query.add_widget(rules_btn)
        self.screen_query.add_widget(screen_name)
        self.screen_query.add_widget(date_en_btn)
        self.screen_query.add_widget(self.selected_date)
        self.screen_query.add_widget(self.minor_rating_label)
        self.screen_query.add_widget(self.severe_rating_label)
        self.screen_query.add_widget(back_btn)

    # ------------ Settings Screen ---------------

    def settings_save(self, sound, notification):
        self.click_sound()
        self.store['data']['Sound'] = sound
        self.store['data']['Notification'] = notification
        self.store['data'] = self.store['data']

        if not notification:
            self.stop_service()
        elif self.service is None:
            self.start_service()

    def settings_screen(self):
        self.screen_settings = Screen(name="settings_scrn")

        if not self.store.exists('data'):
            notification_stat = True
            sound_stat = True
        else:
            notification_stat = self.store.get('data')['Notification']
            sound_stat = self.store.get('data')['Sound']

        screen_name = MDLabel(
            text="Settings", font_style="H4",
            pos_hint={"y": .4}, halign="center"
        )

        notification_switch = MDSwitch(
            pos_hint={"center_y": .65, "x": .75}, active=notification_stat
        )
        notification_label = MDLabel(
            text="Notifications", font_style="H5", pos_hint={"center_y": .655, "x": .15}
        )

        sound_switch = MDSwitch(
            pos_hint={"center_y": .55, "x": .75}, active=sound_stat
        )

        sound_label = MDLabel(
            text="Sound", font_style="H5", pos_hint={"center_y": .555, "x": .15}
        )

        back_btn = MDIconButton(
            icon="arrow-left-drop-circle", pos_hint={"y": 0, "x": 0},
            # icon_size="50sp",
            on_release=lambda *args: self.sm.switch_to(
                self.screen_main, direction='right'),
            on_press=lambda *args: self.settings_save(
                sound_switch.active, notification_switch.active)
        )

        self.screen_settings.add_widget(screen_name)
        self.screen_settings.add_widget(back_btn)
        self.screen_settings.add_widget(sound_switch)
        self.screen_settings.add_widget(notification_switch)
        self.screen_settings.add_widget(notification_label)
        self.screen_settings.add_widget(sound_label)

    # --------------- TIPS Screen -------------------

    def tips_screen(self):
        self.screen_tips = Screen(name="tips_scrn")

        screen_name = MDLabel(
            text="Tips", font_style="H4",
            pos_hint={"y": .4}, halign="center"
        )

        general_tips_txt = MDDialog(
            title="General Tips",
            text=GENERAL_TIPS,
            width_offset='10dp'
        )
        before_eq_txt = MDDialog(
            title="Before Earthquake",
            text=BEFORE_EQ,
            width_offset='10dp'
        )
        during_eq_txt = MDDialog(
            title="During Earthquake",
            text=DURING_EQ,
            width_offset='10dp'
        )
        after_eq_txt = MDDialog(
            title="After Earthquake",
            text=AFTER_EQ,
            width_offset='10dp'
        )

        general_tips = MDRectangleFlatIconButton(
            text="[b]General Tips[/b]", pos_hint={"center_y": .65, "center_x": .5},
            icon='information-outline', text_color=self.btn_color, line_color=self.btn_color,
            # theme_icon_color="Custom",
            icon_color=self.btn_color,
            on_release=general_tips_txt.open, on_press=self.click_sound
        )
        before_eq = MDRectangleFlatIconButton(
            text="[b]Before an Earthquake[/b]", pos_hint={"center_y": .55, "center_x": .5},
            text_color=self.btn_color, line_color=self.btn_color,
            # theme_icon_color="Custom",
            icon_color=self.btn_color, on_release=before_eq_txt.open, icon="walk",
            on_press=self.click_sound
        )
        during_eq = MDRectangleFlatIconButton(
            text="[b]During an Earthquake[/b]", pos_hint={"center_y": .45, "center_x": .5},
            text_color=self.btn_color, line_color=self.btn_color,
            # theme_icon_color="Custom",
            icon_color=self.btn_color, on_release=during_eq_txt.open, icon="run",
            on_press=self.click_sound
        )
        after_eq = MDRectangleFlatIconButton(
            text="[b]After an Earthquake[/b]", pos_hint={"center_y": .35, "center_x": .5},
            text_color=self.btn_color, line_color=self.btn_color,
            # theme_icon_color="Custom",
            icon_color=self.btn_color, on_release=after_eq_txt.open, icon="human-male",
            on_press=self.click_sound
        )

        back_btn = MDIconButton(
            icon="arrow-left-drop-circle", pos_hint={"y": 0, "x": 0},
            # icon_size="50sp",
            on_release=lambda *args: self.sm.switch_to(
                self.screen_main, direction='right'),
            on_press=self.click_sound
        )

        self.screen_tips.add_widget(general_tips)
        self.screen_tips.add_widget(before_eq)
        self.screen_tips.add_widget(during_eq)
        self.screen_tips.add_widget(after_eq)

        self.screen_tips.add_widget(screen_name)
        self.screen_tips.add_widget(back_btn)

    # -------------- Region Selection ---------------

    def save_data(self, date):
        date = int(date)

        dateBD = int(datetime.now(timezone('UTC')).astimezone(
            timezone('Europe/London')).strftime("%d"))

        delta = dateBD - date

        self.store.put('data', Sound=True, Notification=True, Time=delta)
        self.sm.switch_to(self.screen_main, direction='left')
        self.click_sound()

        with open("./files/today_date.txt", 'w') as f:
            f.write(str(dateBD - 1).zfill(2))

        if platform == 'android':
            self.start_service()

    def country_selection_screen(self):

        now_utc = datetime.now(timezone('UTC'))

        self.screen_country_selection = Screen(name="country_selection_scrn")

        screen_name = MDLabel(
            text="Getting your\nLocation", font_style="H4",
            pos_hint={"y": .40}, halign="center"
        )

        location_img = Image(
            source="./assets/location.png", pos_hint={"center_y": .6, "center_x": .5}, size_hint=(.5, .5)
        )

        location_stat = MDLabel(
            pos_hint={"center_y": .3}, halign="center", markup=True
        )

        TimeZone = autoclass('java.util.TimeZone')
        time_zone_name = TimeZone.getDefault().getID()

        now_time = now_utc.astimezone(timezone(time_zone_name))
        date = now_time.strftime("%d")

        location_confirm_btn = MDFillRoundFlatButton(
            text="   Done   ", pos_hint={"center_x": .5, "center_y": .08}, md_bg_color=self.btn_color,
            on_release=lambda *args: self.save_data(date)
        )

        location_stat.text = f"Your Time Zone\n\n[size=25sp]{time_zone_name}[/size]\nUTC {now_time.strftime('%z')}"

        self.screen_country_selection.add_widget(screen_name)
        self.screen_country_selection.add_widget(location_img)
        self.screen_country_selection.add_widget(location_stat)
        self.screen_country_selection.add_widget(location_confirm_btn)

    # ----------- Clicked Sound --------------

    def click_sound(self, *args):
        if self.store.get('data')['Sound']:
            self.sound.play()

    def build(self):

        self.service = None

        self.sm = ScreenManager()

        self.main_screen()
        self.query_screen()
        self.settings_screen()
        self.tips_screen()
        self.country_selection_screen()

        self.sm.add_widget(self.screen_main)
        self.sm.add_widget(self.screen_query)
        self.sm.add_widget(self.screen_settings)
        self.sm.add_widget(self.screen_country_selection)

        if not self.store.exists('data'):
            self.sm.current = 'country_selection_scrn'

        elif platform == 'android':
            if self.store.get('data')['Notification']:
                self.start_service()

        return self.sm


MainApp().run()

# search_bar = MDTextField(
#     icon_right='magnify', size_hint=(.8, 1),
#     hint_text="Your Country", mode="rectangle", pos_hint={"center_x": 0.5, "y": .75}
# )
