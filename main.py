from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable

from database import Database

db = Database(
    database="postgres",
    user="postgres",
    password="root",
    host="localhost",
    port="5432"
)
db.init()

KV = """
RelativeLayout:
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "WalletWatch"

        MDBoxLayout:
            orientation: "vertical"
            padding: 10

            MDLabel:
                size_hint: (1, None)
                valign: "top"
                id: total_spending
                font_style: "H3"
            
            ScrollView:
                id: item_table
            
            MDBoxLayout:
                spacing: 20
                size_hint: (1, None)

                MDTextField:
                    id: item_name
                    hint_text: "Name"
                
                MDTextField:
                    id: item_price
                    helper_text: "Please enter a number (Without $)"
                    helper_text_mode: "on_error"
                    size_hint: (0.3, None)
                    hint_text: "Price"
                
                MDFillRoundFlatButton:
                    id: add_button
                    text: "Add to list"
                
                MDTextField:
                    id: item_id
                    helper_text: "Please enter a number"
                    helper_text_mode: "on_error"
                    size_hint: (0.15, None)
                    hint_text: "ID"

                MDFillRoundFlatButton:
                    id: delete_button
                    text: "Delete"
"""

class WalletWatch(MDApp):
    def build(self):
        self.screen = Builder.load_string(KV)

        items = [(item[0], item[1], "$" + str(item[2])) for item in db.get_items()]
        self.item_table = MDDataTable(
            column_data=[
                ("No", dp(30)),
                ("Name", dp(170)),
                ("Price", dp(90))
            ],
            row_data=items,
            rows_num=100,
            background_color_selected_cell="#FFFFFF",
        )
        
        spending = db.total_spending()[0]
        text = f"Your spending: ${spending if spending else '0'}"

        total_label = self.screen.ids.total_spending
        total_label.text = text

        self.screen.ids.item_table.add_widget(self.item_table)
        self.screen.ids.add_button.bind(on_press=self.add_data)
        self.screen.ids.delete_button.bind(on_press=self.delete_data)

        return self.screen
    
    def add_data(self, _):
        name = self.screen.ids.item_name
        price = self.screen.ids.item_price
        total = self.screen.ids.total_spending
        table = self.item_table

        if "$" in price.text:
            price.error = True
            return
        try:
            int(price.text)
        except ValueError:
            price.error = True
            return

        if len(table.row_data) < 1:
            table.add_row((1, name.text, f"${price.text}"))
            db.insert(1, name.text, price.text)

        else:
            last_num_row = int(table.row_data[-1][0])
            table.add_row((last_num_row + 1, name.text, f"${price.text}"))
            db.insert(last_num_row + 1, name.text, price.text)

        name.text = ""
        price.text = ""

        spending = db.total_spending()[0]
        total.text = f"Your spending: ${spending if spending else '0'}"

    def delete_data(self, _):
        item_id = self.screen.ids.item_id
        table = self.item_table
        total = self.screen.ids.total_spending

        try:
            int(item_id.text)
        except ValueError:
            item_id.error = True
            return
        
        data = table.row_data

        for i in range(len(data)):
            if data[i][0] == int(item_id.text):
                db.delete(item_id.text)
                table.remove_row(data[i])
                break

        item_id.text = ""

        spending = db.total_spending()[0]
        total.text = f"Your spending: ${spending if spending else '0'}"

if __name__ == '__main__':
    WalletWatch().run()
    db.close_db()