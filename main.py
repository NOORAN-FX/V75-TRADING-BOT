import tkinter as tk
from gui import TradingBotGUI
from deriv_api import DerivAPI
from analysis_engine import AnalysisEngine
import asyncio

class V75PredictionBot:
    def __init__(self):
        self.gui = TradingGUI()
        self.analysis_engine = AnalysisEngine()
        self.api = DerivAPI()  # Initialize API connection
        self.running = False
        
        # Load initial data
        try:
            initial_data = self.api.get_price_data()
            self.analysis_engine.update_data(initial_data)
        except Exception as e:
            self.gui.show_error(f"Initialization failed: {str(e)}")

    def run(self):
        self.running = True
        try:
            # Start the GUI main loop in a separate thread
            import threading
            gui_thread = threading.Thread(target=self.gui.root.mainloop)
            gui_thread.start()
            
            # Start analysis updates
            self.update_analysis()
            
        except Exception as e:
            self.gui.show_error(f"Runtime error: {str(e)}")

    def update_analysis(self):
        if self.running:
            try:
                # Get fresh market data
                new_data = DerivAPI.get_price_data()
                
                # Update analysis engine
                self.analysis_engine.update_data(new_data)
                prediction = self.analysis_engine.make_prediction()
                
                # Update GUI with new prediction
                self.gui.update(prediction)
                
            except Exception as e:
                self.gui.show_error(str(e))
            
            # Schedule next update (every 10 seconds)
            self.gui.root.after(10000, self.update_analysis)

    async def start(self):
        await self.api.connect()
        self.root.mainloop()

# Add to bottom of file
if __name__ == "__main__":
    try:
        bot = V75PredictionBot()
        bot.run()
    except Exception as e:
        print(f"Application failed to start: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("Application shutdown")
    asyncio.run(bot.start())