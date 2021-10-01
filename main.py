import requests
import json
import datetime as dt
import kivy
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.gridlayout import GridLayout
from kivy.factory import Factory
from kivy.uix.popup import Popup

class EventType:
    def __init__(self, day, month, year, title):
        self.day = day
        self.month = month
        self.year = year
        self.title = title

class TaskPopup(GridLayout):
    textInput = ObjectProperty(None)

    def newTask(self):
        if (self.textInput.text != ""):
            task = self.textInput.text
            App.get_running_app().root.ids.taskList.items.append(task)
            App.get_running_app().root.ids.taskList.updateList()
            self.textInput.text = ""

class EventPopup(GridLayout):
    dayInput = ObjectProperty(None)
    monthInput = ObjectProperty(None)
    yearInput = ObjectProperty(None)
    eventInput = ObjectProperty(None)

    def newEvent(self):
        if (self.eventInput.text != "" and self.dayInput.text != "" and self.monthInput.text != "" and self.yearInput.text != ""):
            event = EventType(int(self.dayInput.text), int(self.monthInput.text), int(self.yearInput.text), self.eventInput.text)
            App.get_running_app().root.ids.eventList.items.append(event)
            App.get_running_app().root.ids.eventList.updateList()
            self.eventInput.text = ""
            self.dayInput.text = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.yearInput.text = str(dt.date.today().year)
        self.monthInput.text = str(dt.date.today().month)

class RVItem(Factory.Button):
    taskField = ObjectProperty(None)
    eventField = ObjectProperty(None)

    def get_data_index(self):
        return self.parent.get_view_index_at(self.center)
    @property
    def rv(self):
        return self.parent.parent
    def on_press(self):
        self.rv.data.pop(self.get_data_index())
        self.rv.items.pop(self.get_data_index())
        self.rv.updateList()

class TaskListWidget(RecycleView):
    firebase_tasks_url = "https://kivynotes-c4ece-default-rtdb.europe-west1.firebasedatabase.app/-MkWEbhsC3Wwci-Us-Bv/Tasks/.json"
    def updateList(self):
        self.data = []
        for item in self.items:
            self.data.append({"text": str(item), "background_color": (0.2, 0.8, 1, 1), "font_size": 40})
        print("__Task List Updated__")
        self.updateDatabase()

    def updateDatabase(self):
        itemDict = dict.fromkeys(self.items, "T")
        print(itemDict)
        requests.put(url=self.firebase_tasks_url, json=json.loads(json.dumps(itemDict)))
        print("__Task Database Updated__")

    def loadDatabase(self):
        json_data = requests.get(url=self.firebase_tasks_url)
        dataDict = json_data.json()
        if (dataDict != None):
            for key in dataDict:
                self.items.append(key)
            self.updateList()
        print("__Task Database Loaded__")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.items = []
        self.loadDatabase()

class EventListWidget(RecycleView):
    firebase_events_url = "https://kivynotes-c4ece-default-rtdb.europe-west1.firebasedatabase.app/-MkWEbhsC3Wwci-Us-Bv/Events/.json"
    def updateList(self):
        self.items.sort(key=lambda x: (x.month*100+x.day+x.year*100))
        self.data = []
        for item in self.items:
            if (item.year == dt.date.today().year):
                self.data.append({"text": "("+str(item.day)+"."+str(item.month)+".) "+str(item.title),
                                  "background_color": (1, 0.6, 1, 1), "font_size": 40})
            else:
                self.data.append({"text": "(" + str(item.day) + "." + str(item.month) +"."+ str(item.year)+") " + str(item.title),
                                  "background_color": (1, 0.6, 1, 1), "font_size": 40})

        print("__Event List Updated__")
        self.updateDatabase()

    def updateDatabase(self):
        itemDict = {}
        for item in self.items:
            nested = {}
            nested['day'] = item.day
            nested['month'] = item.month
            nested['year'] = item.year
            nested['title'] = item.title
            itemDict[item.title] = nested
            print(nested)
        print(itemDict)
        print("event update dict: ")
        print(json.dumps(itemDict))
        requests.put(url=self.firebase_events_url, json=json.loads(json.dumps(itemDict)))
        print("__Event Database Updated__")

    def loadDatabase(self):
        json_data = requests.get(url=self.firebase_events_url)
        dataDict = json_data.json()
        if (dataDict != None):
            for key in dataDict:
                self.items.append(EventType(int(dataDict[key]['day']), int(dataDict[key]['month']), int(dataDict[key]['year']), dataDict[key]['title']))
                print(dataDict[key]['day'], dataDict[key]['month'], dataDict[key]['year'], dataDict[key]['title'])
            self.updateList()
        print("__Event Database Loaded__")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.items = []
        self.loadDatabase()

class MyGrid(GridLayout):
    taskField = ObjectProperty(None)
    eventField = ObjectProperty(None)

    def show_task_popup(self):
        show = TaskPopup()
        popupWindow = Popup(title="Task Adder", content=show, size_hint=(0.85, 0.3))
        popupWindow.open()
        print("task popup opened")

    def show_event_popup(self):
        show = EventPopup()
        popupWindow = Popup(title="Event Adder", content=show, size_hint=(0.85, 0.4))
        popupWindow.open()
        print("event popup opened")

class MyApp(App):
    def build(self):
        self.title = 'MaroNoteS'
        return MyGrid()

if __name__ == "__main__":
    MyApp().run()