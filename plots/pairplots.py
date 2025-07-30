import plotly.express as px
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class RenderPairplot:

    def __init__(self,
                 df_input=pd.DataFrame,
                 export_dir: str = '/mnt/mls/exports',
                 quantile: float = .02,
                 dimensions: tuple = (1600, 1200)) -> None:
        self.__df = df_input
        self.__export_dir = export_dir
        self.__quantile = quantile
        self.__dimensions = dimensions

    def plotly(self, quantile: float = None, dimensions: tuple = None) -> None:
        # Use class-level values if parameters are not provided
        quantile = quantile if quantile is not None else self.__quantile
        dimensions = dimensions if dimensions is not None else self.__dimensions

        # Create pair plot using Plotly (first X% of data)
        fig = px.scatter_matrix(
            self.__df[:int(len(self.__df) * quantile)],  # Match Seaborn subset behavior
            dimensions=self.__df.columns  # Ensure all columns are plotted
        )

        # Update marker styling
        fig.update_traces(marker=dict(size=6, line=dict(width=1, color='black')))

        # Increase figure size
        fig.update_layout(
            width=dimensions[0],
            height=dimensions[1],
            margin=dict(l=50, r=50, t=50, b=50),
        )

        # Ensure export folder exists
        os.makedirs(self.__export_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")

        # Save as an interactive HTML file
        html_export_path = os.path.join(self.__export_dir, f"{timestamp}_pairplot_plotly.html")
        fig.write_html(html_export_path)

        # Save as an image (high resolution)
        image_export_path = os.path.join(self.__export_dir, f"{timestamp}_pairplot_plotly.png")
        fig.write_image(image_export_path, scale=3)

        # Display the plot in the Jupyter Notebook
        display(fig)

        print(f"Pairplot saved as interactive HTML: {html_export_path}")
        print(f"Pairplot saved as image: {image_export_path}")

    def seaborn(self, quantile: float = None, dimensions: tuple = None) -> None:
        # Use class-level values if parameters are not provided
        quantile = quantile if quantile is not None else self.__quantile
        dimensions = dimensions if dimensions is not None else self.__dimensions

        # Subset first X% of the DataFrame
        df_subset = self.__df[:int(len(self.__df) * quantile)]

        # Set figure size to match Plotly
        plt.figure(figsize=(dimensions[0] / 100, dimensions[1] / 100))

        # Create pairplot with styling to match Plotly
        pairplot = sns.pairplot(
            df_subset,
            plot_kws={"s": 36, "edgecolor": "black", "linewidth": 1},  # Match marker size & border
        )

        # Ensure export folder exists
        os.makedirs(self.__export_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")

        # Save as high-resolution PNG (scale=3 equivalent to dpi=300)
        image_export_path = os.path.join(self.__export_dir, f"{timestamp}_pairplot_seaborn.png")
        pairplot.savefig(image_export_path, dpi=300)

        print(f"Pairplot saved as image: {image_export_path}")