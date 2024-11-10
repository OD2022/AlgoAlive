import wx
import wx.grid




class StatisticsPanel(wx.Panel):
    def __init__(self, parent, scheduler): 
        super().__init__(parent)
        self.scheduler = scheduler
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.create_statistics()

    def create_statistics(self):
        if self.scheduler is not None and self.scheduler.final_stats is not None:
            final_stats = self.scheduler.final_stats
            
            # Get headers
            headers = ['Process ID', 'Arrival Time', 'Execution Time', 'Completion Time', 'Waiting Time', 'Turnaround Time']
            
            # Get data
            data = []
            total_waiting_time = 0
            total_turnaround_time = 0
            for process_id, stats in final_stats.items():
                arrival_time = stats['arrival_time']
                execution_time = stats['execution_time']
                completion_time = stats['completion_time']
                waiting_time = completion_time - arrival_time - execution_time
                turnaround_time = completion_time - arrival_time
                data.append([process_id, arrival_time, execution_time, completion_time, waiting_time, turnaround_time])
                total_waiting_time += waiting_time
                total_turnaround_time += turnaround_time
            
            # Calculate overall average statistics
            num_processes = len(final_stats)
            overall_average_waiting_time = total_waiting_time / num_processes
            overall_average_turnaround_time = total_turnaround_time / num_processes
            
            # Create a grid
            grid = wx.grid.Grid(self)
            grid.CreateGrid(len(data) + 1, len(headers))  # +1 for the overall average row
            
            # Set headers
            for col, header in enumerate(headers):
                grid.SetColLabelValue(col, header)
            
            # Set data
            for row, row_data in enumerate(data):
                for col, value in enumerate(row_data):
                    grid.SetCellValue(row, col, str(value))
            
            # Set column sizes
            for col in range(len(headers)):
                grid.SetColSize(col, 100)  # Set the width to 200 pixels
            
            # Set overall average row
            grid.SetCellValue(len(data), 0, "Overall Average")
            grid.SetCellValue(len(data), 4, str(overall_average_waiting_time))
            grid.SetCellValue(len(data), 5, str(overall_average_turnaround_time))
            
            # Add grid to sizer
            self.sizer.Add(grid, 1, wx.EXPAND)
