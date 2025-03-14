# Anime Dashboard

An interactive dashboard for exploring anime data using Streamlit and the Jikan API v4.

## Features

- **Anime Discovery Engine**: Search and filter anime by title, score, and type with detailed visualizations and insights
- **Elite Anime Rankings**: Explore top-rated anime with multiple category filters and comprehensive analytics
- **Anime Comparison Engine**: Compare two anime side by side with detailed statistical analysis and content breakdowns
- **Responsive Design**: Optimized for both desktop and mobile viewing
- **Data Export**: Download search results and comparison data as CSV files

## Advanced Features

- **API Rate Limiting**: Implements proper rate limiting for Jikan API (3 requests/second, 60/minute)
- **Error Handling**: Robust error handling for API requests with fallback mechanisms
- **Data Caching**: Caches search suggestions to improve performance (TTL: 5 minutes)
- **Mobile Detection**: Automatically adjusts layout based on device type
- **Search Insights**: Provides statistical insights about search results
- **Time Investment Analysis**: Calculates approximate viewing time required for each anime

## Components Used

1. **Navigation**
   - Radio buttons (View Selection)
   - Sidebar with about section toggle

2. **Search & Filtering**
   - Text Input with auto-suggestions
   - Slider for score filtering
   - Multiselect for type filtering
   - Selectbox for category selection

3. **Layout & Organization**
   - Columns for side-by-side layout
   - Containers for grouping related elements
   - Expanders for collapsible sections
   - Dividers for visual separation

4. **Data Visualization**
   - Interactive Plotly histograms
   - Pie charts for distribution analysis
   - Scatter plots with hover information
   - Progress bars for comparative metrics

5. **User Experience**
   - Spinners for loading states
   - Info/warning messages for user guidance
   - Captioned headers with emoji icons
   - Help guides in expandable sections
   - Download buttons for data export

6. **Data Management**
   - Session state for persistent selections
   - Cached data functions
   - Dataframes with custom formatting
   - Metrics for key statistics

## Live Demo

Access the live dashboard here: [Anime Dashboard](https://ds29-day40-alfina-nurmayati-build-portofolio-with.streamlit.app)

## Data Source

Data is fetched from [MyAnimeList](https://myanimelist.net/) using the [Jikan API v4](https://docs.api.jikan.moe/).

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- Requests
- Logging

## Code Structure

The application is organized into three main views:
1. **Search Anime**: Provides a flexible search interface with filters and visualizations
2. **Top Anime**: Presents top-ranked anime with category filters and interactive charts
3. **Compare Anime**: Enables side-by-side comparison of two anime with statistical analysis

## License

MIT License 