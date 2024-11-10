import wx
import wx.grid
import sys
import copy
import re


from GanttPanel import GanttPanel
from Process import Process
from ReadOnlyDict import ReadOnlyDict
from RoundRobin_Scheduler import RoundRobin_Scheduler
from PreemptiveSJF_Scheduler import Preemptive_SJF_Scheduler
from StatisticsPanel import StatisticsPanel
from MLFQ_Scheduler import MLFQ_Scheduler


user_processes = []

class ProcessInputDialog(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)

        self.colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF', '#800000', '#008000', '#000080', '#808000']

        self.SetSize((600, 400))  

        sizer = wx.BoxSizer(wx.VERTICAL)

        grid = wx.grid.Grid(self)
        grid.CreateGrid(10, 2) 
        grid.SetColLabelValue(0, "Arrival Time")
        grid.SetColLabelValue(1, "Execution Time")

        font = grid.GetDefaultCellFont()
        font.SetPointSize(14)
        grid.SetDefaultCellFont(font)
        grid.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        grid.SetColSize(0, 150)  
        grid.SetColSize(1, 150)  

        for i in range(10):
            grid.SetRowSize(i, 40)  

        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, border=5)

        btn_ok = wx.Button(self, wx.ID_OK, label="OK")
        btn_ok.SetBackgroundColour(wx.Colour(0, 255, 0))  
        btn_ok.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        btn_cancel = wx.Button(self, wx.ID_CANCEL, label="Cancel")
        btn_cancel.SetBackgroundColour(wx.Colour(255, 0, 255))  
        btn_cancel.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_box.Add(btn_ok, 0, wx.ALL, 5)
        btn_box.Add(btn_cancel, 0, wx.ALL, 5)

        sizer.Add(btn_box, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(sizer)
        self.grid = grid
        btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)
        btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)


    def show_error_dialog(self, message):
        dlg = wx.MessageDialog(None, message, 'Error', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()


    def on_ok(self, event):
        for i in range(10):
            arrival_text = self.grid.GetCellValue(i, 0).strip() 
            execution_text = self.grid.GetCellValue(i, 1).strip()
            if not arrival_text or not execution_text:
                continue
            
            # Validating arrival and execution times using regular expressions
            if not re.match(r'^\d*$', arrival_text) or not re.match(r'^\d*$', execution_text):
                error_message = "Arrival and execution times should only contain digits and spaces."
                self.show_error_dialog(error_message)
                raise ValueError(error_message)
            
            arrival = int(arrival_text)
            execution = int(execution_text)
            if arrival < 0 or execution < 0:
                error_message = "Arrival and execution times cannot be negative."
                self.show_error_dialog(error_message)
                raise ValueError(error_message)
            
            color = self.colors[i]
            user_processes.append(Process(len(user_processes) + 1, arrival, execution, color))
            self.EndModal(wx.ID_OK)


    def on_cancel(self, event):
            self.GetParent().Close()  
            self.EndModal(wx.ID_CANCEL)  
            sys.exit()



class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Scheduling Simulation", size=(1000, 800))
        self.panel = wx.Panel(self)
        self.main_box = wx.BoxSizer(wx.VERTICAL)

        dlg = ProcessInputDialog(self, "Process Input")
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()

        self.scheduler_buttons = []
        self.rr_button = wx.Button(self.panel, label="Round Robin")
        self.preemptive_sjf_button = wx.Button(self.panel, label="Preemptive SJF")
        self.mlfq_button = wx.Button(self.panel, label="Multi-level Feeback Queue")


        self.rr_button.Bind(wx.EVT_BUTTON, self.on_rr)
        self.preemptive_sjf_button.Bind(wx.EVT_BUTTON, self.on_preemptive_sjf)
        self.mlfq_button.Bind(wx.EVT_BUTTON, self.on_mlfq)

        self.scheduler_buttons.extend([self.rr_button, self.preemptive_sjf_button, self.mlfq_button])

        button_box = wx.BoxSizer(wx.HORIZONTAL)
        for button in self.scheduler_buttons:
            button_box.Add(button, 1, wx.EXPAND | wx.ALL, border=5)

        self.main_box.Add(button_box, 0, wx.EXPAND | wx.ALL, border=5)

        scrolled_window = wx.ScrolledWindow(self.panel)
        scrolled_window.SetScrollbars(1, 1, 1, 1)
        scrolled_window_sizer = wx.BoxSizer(wx.VERTICAL)

        self.gantt_panel = GanttPanel(scrolled_window, None)
        self.statistics_panel = StatisticsPanel(scrolled_window, None)

        scrolled_window_sizer.Add(self.gantt_panel, 0, wx.EXPAND | wx.ALL, border=5)
        scrolled_window_sizer.Add(self.statistics_panel, 0, wx.EXPAND | wx.ALL, border=5)

        scrolled_window.SetSizer(scrolled_window_sizer)

        self.main_box.Add(scrolled_window, 1, wx.EXPAND | wx.ALL, border=5)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.panel.SetSizer(self.main_box)
        self.Layout()


    def on_close(self, event):
        print("Goodbye")
        sys.exit()

    def on_rr(self, event):
        processes = self.generate_processes()
        self.create_scheduler(lambda: RoundRobin_Scheduler(2), processes)

    def on_preemptive_sjf(self, event):
        processes = self.generate_processes()
        self.create_scheduler(Preemptive_SJF_Scheduler, processes)


    def on_mlfq(self, event):
        processes = self.generate_processes()
        self.create_scheduler(MLFQ_Scheduler, processes)


    def generate_processes(self):
        return copy.deepcopy(user_processes)


    def create_scheduler(self, scheduler_class, processes):
        if self.gantt_panel:
            self.gantt_panel.Destroy()
        if self.statistics_panel:
            self.statistics_panel.Destroy()
        self.current_scheduler = scheduler_class()
        for process in processes:
            self.current_scheduler.add_process(process)
        self.gantt_panel = self.current_scheduler.create_gantt_chart_panel(self.panel)
        self.main_box.Add(self.gantt_panel, 0, wx.EXPAND | wx.ALL, border=5)
        self.panel.Layout()
        self.update_gantt_chart()
        self.update_statistics()
     

    def update_gantt_chart(self):
        if self.current_scheduler and self.gantt_panel:
            gantt_data = []
            while True:
                current_process = self.current_scheduler.execute_next_process()
                if current_process is None:
                    break
                gantt_data.append({'start': current_process.begin_exec_time, 'duration': current_process.alloted_time, 'process_id': current_process.process_id, 'color': current_process.color, 'queue': current_process.currentQueue})
            self.gantt_panel.update_gantt_chart(gantt_data)


    def update_statistics(self):
            self.statistics_panel = StatisticsPanel(self.panel, self.current_scheduler)
            self.main_box.Add(self.statistics_panel, 0, wx.EXPAND | wx.ALL, border=5)
            self.panel.Layout()

        
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
