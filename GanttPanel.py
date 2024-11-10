import wx
import wx.grid
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import time



class GanttPanel(wx.Panel):
    def __init__(self, parent, scheduler):
        super().__init__(parent)
        self.scheduler = scheduler
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)


    def update_gantt_chart(self, gantt_data):
        ax = self.figure.add_subplot(111)
        ax.clear()
        yticks = [0.5]
        labels = ['']
        colors = []
        total_duration = sum(p['duration'] for p in gantt_data)

   
        ax.set_xticks(range(0, total_duration+1, 1))
        ax.set_xticklabels(range(0, total_duration+1, 1))

        for i, p in enumerate(gantt_data):
            color = p['color']
            colors.append(color)
            ax.broken_barh([(p['start'], p['duration'])], (i, 1), facecolors=color)


            text_x = p['start'] + p['duration'] / 2
            text_y = i + 0.5
            ax.text(text_x, text_y, f'P{p["process_id"]}:Q{p["queue"]}', color='black', fontsize=6,  ha='center', va='center')
            yticks.append(i + 1)
            labels.append(f'P{p["process_id"]}')  
            
            # Drawing the current process
            ax.set_yticks(yticks)
            ax.set_yticklabels(labels)
            ax.set_xlabel('Time')
            ax.set_ylabel('Processes')
            ax.set_title('Gantt Chart')
            ax.grid(True)
            self.canvas.draw()
            
            time.sleep(0.3) 