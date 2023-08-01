from random import choice
import os
import pygsheets



class RestaurantPicker:
    def __init__(self, chatroom_id:str):
        self.reply_msg = ''
        
        # google worksheet
        gc = pygsheets.authorize(service_account_env_var="GOOGLE_SECRET_KEY")

        sheet_url = os.environ.get("GOOGLE_SHEET_URL")
        sheet = gc.open_by_url(sheet_url)
        
        # 開啟worksheet by名稱
        try:
            self.work_sheet = sheet.worksheet_by_title(chatroom_id)

        # 若沒有則create一個新的worksheet
        except pygsheets.SpreadsheetNotFound:
            self.work_sheet = sheet.add_worksheet(chatroom_id)
            # 只會使用到A跟B的column
            self.work_sheet.update_value("A1", "restaurant picker")
            self.work_sheet.update_value("B1", "drinks picker") # TODO: add drinks functions
    
    
    def help(self):
        self.reply_msg = "\
說明: 在難以選擇要吃什麼的時候，幫您做出客觀的決定\n\n\
指令: -商家 -新增(add)    商家 (商家2 ...)\n\
           -移除(delete) 商家 (商家2 ...)\n\
           -抽(pick)  (不允許 商家 ...)\n\
                      (允許 商家 ...)\n\
           -列出(list)"
        
        # print(self.reply_msg)
        

    def add(self, restaurants:list):
        r = self.work_sheet.get_col(1, include_tailing_empty=False)[1:]
        r_cols = len(r) + 1

        if restaurants != []:
            new = list()
            
            for restaurant in restaurants:
                if restaurant not in r:
                    r.append(restaurant)
                    new.append(restaurant)

            for i in range(len(new)):
                self.work_sheet.update_value(f"A{r_cols + i + 1}", new[i])
                self.reply_msg += f"{new[i]} 新增成功\n"
            
            self.reply_msg = self.reply_msg[0:-1]
        
        else:
            self.reply_msg = "商家不能為空"
    
    def delete(self, restaurants:list):
        r = self.work_sheet.get_col(1, include_tailing_empty=False)[1:]
        r_cols = len(r) + 1
        
        if r_cols == 1:
            self.reply_msg = "Nothing to delete"
            
        elif restaurants != []:
            deleted = list()
            
            for restaurant in restaurants:
                if restaurant in r:
                    r.remove(restaurant)
                    deleted.append(restaurant)
            
            self.work_sheet.clear(start="A2", end=f"A{r_cols}")
            
            for i in range(0, len(r)):
                self.work_sheet.update_value(f"A{1 + (i+1)}", r[i])
            
            for i in range(len(deleted)):
                self.reply_msg += f"{deleted[i]} 移除成功\n"
            
            self.reply_msg = self.reply_msg[0:-1]
            
        else:
            self.reply_msg = "商家不能為空"

    def pick(self, command:list):
        r = self.work_sheet.get_col(1, include_tailing_empty=False)[1:]
        
        to_pick = [x for x in r]
        error = False
        
        if command != []:
            try:
                if command[0] == "不允許":
                    for restaurant in command[1:]:
                        if restaurant in to_pick:
                            to_pick.remove(restaurant)
                elif command[0] == "允許":
                    to_pick.clear()
                    for restaurant in command[1:]:
                        to_pick.append(restaurant)
                else:
                    self.reply_msg = "指令名稱錯誤"
                    error = True
                
                if to_pick == []:
                    error = True
                    self.reply_msg = "選項為零，無法選擇"
            
            except IndexError:
                self.reply_msg = "指令格式錯誤"
                error = True
        
        if not error:
            print(to_pick)
            ans = choice(to_pick)
            self.reply_msg = ans

    def show_all(self):
        r = self.work_sheet.get_col(1, include_tailing_empty=False)[1:]
        
        for i in r:
            self.reply_msg += f"{i}\n"
            
        self.reply_msg = self.reply_msg[0:-1]

    def main(self, msg:list):
        # determine what user wants to do
        try:    
            if msg[1] == "help":
                self.help()
            
            elif msg[1] == "新增" or msg[1] == "add":
                self.add(msg[2:])
            
            elif msg[1] == "移除" or msg[1] == "delete":
                self.delete(msg[2:])
            
            elif msg[1] == "抽" or msg[1] == "pick":
                self.pick(msg[2:])
            
            elif msg[1] == "列出" or msg == "list":
                self.show_all()
        
        except:
            self.reply_msg = "指令不完整"
        
        return self.reply_msg


# test = RestaurantPicker("工作表1")
# test.help()