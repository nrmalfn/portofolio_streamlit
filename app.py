"""
Anime Dashboard - A Streamlit application for exploring anime data using the Jikan API.

This application allows users to:
1. Search for anime by title and filter by score and type
2. Browse top anime with various filters
3. Compare two anime side by side

The app uses the Jikan API v4 (https://jikan.moe/), which is a free, open-source API
for MyAnimeList.net. The application demonstrates how to build interactive data
visualizations with Streamlit, Plotly, and handle API interactions with proper
rate limiting and error handling.

Author: Developer
License: MIT
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import logging
import time

# Setup logging to track API calls and application flow
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Jikan API v4 base URL
JIKAN_API_URL = "https://api.jikan.moe/v4"

def rate_limited_request(url, params=None):
    """
    Make a rate-limited request to the Jikan API with proper error handling.
    
    The Jikan API has rate limits of 3 requests per second and 60 per minute.
    This function implements a 1-second delay between requests to respect these limits.
    
    Args:
        url (str): The API endpoint URL
        params (dict, optional): Query parameters for the request
        
    Returns:
        dict: The JSON response from the API
        
    Raises:
        Exception: If the API request fails
    """
    try:
        logger.info(f"Making API request to: {url} with params: {params}")
        time.sleep(1)  # Rate limit: max 3 requests per second
        response = requests.get(url, params=params)
        logger.info(f"API response status: {response.status_code}")
        
        json_data = response.json()
        logger.info(f"API returned data with keys: {json_data.keys()}")
        
        # Jikan API may return 200 status with error details instead of data
        if 'error' in json_data and not json_data.get('data'):
            error_msg = json_data.get('messages', {}).get('error', str(json_data.get('error')))
            logger.error(f"API returned error: {error_msg}")
            # Retry with simpler parameters if this was a search
            if 'q' in params and len(params) > 1:
                logger.info("Retrying with simplified parameters")
                return rate_limited_request(url, {'q': params['q']})
            return json_data
            
        if 'data' in json_data:
            logger.info(f"API returned {len(json_data['data'])} results")
        
        return json_data
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise Exception(f"Failed to fetch data: {str(e)}")

# Configure the Streamlit page with responsive design options
st.set_page_config(
    page_title="Anime Dashboard",
    page_icon="🎬",
    layout="wide"  # Use wide layout for better visualization display
)

# Main title for the dashboard
st.title("Anime Dashboard")

def is_mobile():
    """
    Detect if the application is being viewed on a mobile device.
    
    This function checks if a mobile view parameter is set in the session state
    or in the query parameters. This allows for responsive design adjustments.
    
    Returns:
        bool: True if the app is being viewed on a mobile device, False otherwise
    """
    try:
        return st.session_state.get('mobile_view', 
            st.query_params().get('mobile', ['false'])[0] == 'true')
    except:
        return False

# Adjust chart height based on view type (mobile or desktop)
chart_height = 300 if is_mobile() else 500

# Navigation sidebar with main view options
# Component 1: Radio buttons for selecting the main view
view_mode = st.sidebar.radio(
    "Select View",
    ["Search Anime", "Top Anime", "Compare Anime"]
)

# =====================================================================
# SEARCH ANIME VIEW - Allows users to search for anime by title
# =====================================================================
if view_mode == "Search Anime":
    logger.info(f"Accessing Search Anime view")
    
    # Add header and description
    st.header("🔍 Anime Discovery Engine", divider="rainbow")
    st.caption("Find hidden gems and popular titles matching your preferences")
    
    # Add search guide
    with st.expander("💡 How to use this search"):
        st.markdown("""
        This search helps you:
        1. Find anime that match your taste profile
        2. Discover trends in specific genres/types
        3. Compare popularity vs quality metrics
        
        **Pro Tip:** Combine filters to narrow down results!
        """)
    
    # Component 2: Text Input for anime title search
    search_query = st.text_input("Search Anime", "")
    
    # Component 3: Slider for filtering results by minimum score
    min_score = st.slider("Minimum Score", 0.0, 10.0, 5.0, 0.1)
    
    # Component 4: Multiselect for filtering by anime type
    # Display user-friendly labels while using correct API values
    anime_types_display = ["TV", "Movie", "OVA", "Special", "ONA", "Music"]
    anime_types_api = ["tv", "movie", "ova", "special", "ona", "music"]
    selected_types_display = st.multiselect(
        "Select Anime Types",
        anime_types_display,
        ["TV"]
    )
    
    # Convert display values to API values for the request
    selected_types_api = [anime_types_api[anime_types_display.index(t)] for t in selected_types_display]
    
    # Show active search parameters
    if search_query:
        st.info(
            f"🎯 Current Search: **{search_query}** | Minimum Rating: **{min_score}** | "
            f"Types: **{', '.join(selected_types_display) or 'Any'}**",
            icon="ℹ️"
        )
    
    # Execute search when a query is provided
    if search_query:
        try:
            with st.spinner("Searching for anime..."):
                logger.info(f"Searching for anime: {search_query}")
                
                # Prepare API request parameters
                params = {
                    'q': search_query,
                    'sfw': 'true'  # Filter out adult content
                }
                if selected_types_api:
                    params['type'] = ','.join(selected_types_api)
                
                # Debug output for parameters
                logger.info(f"API parameters: {params}")
                
                # Component: Debug section for API troubleshooting
                # if st.checkbox("Debug API Call"):
                #     st.write("Making direct API call for debugging...")
                #     st.write(f"URL: {JIKAN_API_URL}/anime")
                #     st.write(f"Params: {params}")
                #     import requests
                #     direct_response = requests.get(f"{JIKAN_API_URL}/anime", params=params)
                #     st.write(f"Status Code: {direct_response.status_code}")
                #     if direct_response.status_code == 200:
                #         direct_data = direct_response.json()
                #         st.write(f"Response Keys: {direct_data.keys()}")
                #         if 'data' in direct_data:
                #             st.write(f"Found {len(direct_data['data'])} results")
                #             if len(direct_data['data']) > 0:
                #                 st.write("First result:")
                #                 st.json(direct_data['data'][0])
                #         else:
                #             st.error(f"API Error Response: {direct_data}")
                #     else:
                #         st.error(f"API Error: {direct_response.text}")
                    
                #     # Try alternative search without filters
                #     st.write("Trying alternative simple search...")
                #     simple_params = {'q': search_query}
                #     simple_response = requests.get(f"{JIKAN_API_URL}/anime", params=simple_params)
                #     st.write(f"Simple search status: {simple_response.status_code}")
                #     if simple_response.status_code == 200:
                #         simple_data = simple_response.json()
                #         if 'data' in simple_data:
                #             st.write(f"Simple search found {len(simple_data['data'])} results")

                # Make the actual API request
                results = rate_limited_request(f"{JIKAN_API_URL}/anime", params=params)
                
                # Handle case where no results are found
                if not results.get('data'):
                    st.warning("No results found. Try a different search term.")
                    logger.warning(f"No results found for query: {search_query}")
                else:
                    # Process results and create a DataFrame for easier manipulation
                    with st.spinner("Processing results..."):
                        df = pd.DataFrame([{
                            'title': anime['title'],
                            'image': anime.get('images', {}).get('jpg', {}).get('image_url', ''),
                            'description': anime.get('synopsis', 'No description available'),
                            'score': anime.get('score', 0),
                            'type': anime.get('type', 'Unknown'),
                            'episodes': anime.get('episodes', 0),
                            'members': anime.get('members', 0)
                        } for anime in results['data']])
                        
                        # Apply minimum score filter to results
                        df = df[df['score'] >= min_score]
                        
                        # Handle case where all results are filtered out
                        if df.empty:
                            st.warning("No results match your filters.")
                            logger.info("No results after filtering")
                        else:
                            # Component 5: Expander for displaying raw results table
                            with st.expander("View Results Table"):
                                # Display results in a more visual way
                                for _, row in df.iterrows():
                                    with st.container():
                                        col1, col2 = st.columns([1, 3])
                                        with col1:
                                            st.image(row['image'], width=150)
                                        with col2:
                                            st.subheader(row['title'])
                                            st.write(f"**Score:** {row['score']} | **Type:** {row['type']} | **Episodes:** {row['episodes']}")
                                            st.write(row['description'])
                                        st.divider()
                            
                            # Create interactive visualizations from the results
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                with st.spinner("Creating score distribution..."):
                                    # Histogram of anime scores
                                    fig1 = px.histogram(
                                        df,
                                        x='score',
                                        title=f'Quality Distribution for "{search_query}"',
                                        nbins=20,
                                        color_discrete_sequence=['#FF4B4B']
                                    )
                                    fig1.update_layout(
                                        height=chart_height,
                                        xaxis_title="IMDb-style Rating (1-10)",
                                        yaxis_title="Number of Titles"
                                    )
                                    st.plotly_chart(fig1, use_container_width=True)
                            
                            with col2:
                                with st.spinner("Creating type distribution..."):
                                    # Pie chart of anime types
                                    fig2 = px.pie(
                                        df,
                                        names='type',
                                        title=f'Format Distribution for "{search_query}"',
                                        color_discrete_sequence=px.colors.qualitative.Set3
                                    )
                                    fig2.update_layout(height=chart_height)
                                    st.plotly_chart(fig2, use_container_width=True)
                                    
                            # Add search insights
                            st.subheader("📊 Search Insights", divider="gray")
                            insight_col1, insight_col2, insight_col3 = st.columns(3)
                            
                            with insight_col1:
                                avg_score = df['score'].mean()
                                st.metric(
                                    "Average Rating",
                                    f"{avg_score:.1f}/10",
                                    help="Average rating of all matching titles"
                                )
                                
                            with insight_col2:
                                most_common_type = df['type'].mode()[0]
                                type_count = df['type'].value_counts()[most_common_type]
                                st.metric(
                                    "Most Common Format",
                                    f"{most_common_type}",
                                    f"{type_count} titles",
                                    help="Most frequent anime format in results"
                                )
                                
                            with insight_col3:
                                total_members = df['members'].sum()
                                st.metric(
                                    "Total Community Size",
                                    f"{total_members:,}",
                                    help="Combined member count across all results"
                                )
        except Exception as e:
            # Handle any errors that occur during the search
            st.error(f"An error occurred while searching: {str(e)}")
            logger.error(f"Error in Search Anime view: {str(e)}")

# =====================================================================
# TOP ANIME VIEW - Shows top ranked anime with various filters
# =====================================================================
elif view_mode == "Top Anime":
    logger.info("Accessing Top Anime view")
    
    st.header("🏆 Elite Anime Rankings", divider="rainbow")
    st.caption("Discover the most acclaimed and popular anime across different categories")
    
    # Enhanced category selection
    top_category = st.selectbox(
        "Select Category",
        ["All Time Best", "Currently Airing", "Most Popular", "Upcoming Releases"]
    )
    
    # Set up parameters based on API documentation
    params = {}
    
    # Map user-friendly categories to API parameters
    category_mapping = {
        "All Time Best": None,  # Default top anime
        "Currently Airing": "airing",
        "Most Popular": "bypopularity",
        "Upcoming Releases": "upcoming"
    }
    
    if top_category != "All Time Best":
        params['filter'] = category_mapping[top_category]
    
    # Additional filters in columns
    col1, col2 = st.columns(2)
    with col1:
        type_options = ["All Types", "TV", "Movie", "OVA", "Special", "ONA", "Music"]
        selected_type = st.selectbox("Format Filter", type_options)
        if selected_type != "All Types":
            params['type'] = selected_type.lower()
    
    with col2:
        min_score = st.slider("Minimum Score", 0.0, 10.0, 7.0, 0.1)
    
    try:
        with st.spinner("Loading top anime..."):
            # Get top anime data from the API
            results = rate_limited_request(f"{JIKAN_API_URL}/top/anime", params=params)
            
            if not results.get('data'):
                st.warning("Unable to fetch top anime at the moment.")
                logger.warning("No data received from top anime API")
            else:
                # Create a DataFrame from the API results with enhanced metadata
                df = pd.DataFrame([{
                    'title': anime['title'],
                    'score': anime.get('score', 0),
                    'members': anime.get('members', 0),
                    'rank': anime.get('rank', 0),
                    'type': anime.get('type', 'Unknown'),
                    'episodes': anime.get('episodes', 'N/A'),
                    'status': anime.get('status', 'Unknown'),
                    'year': anime.get('year', 'Unknown'),
                    'image_url': anime.get('images', {}).get('jpg', {}).get('image_url', '')
                } for anime in results['data']])
                
                # Apply score filter
                df = df[df['score'] >= min_score]
                
                if df.empty:
                    st.warning("No anime match your current filters.")
                else:
                    # Display top anime in a clean table format
                    st.subheader("📊 Rankings Overview", divider="gray")
                    
                    # Format the table with custom columns
                    formatted_df = df[['rank', 'title', 'score', 'type', 'episodes', 'status']].copy()
                    formatted_df.columns = ['Rank', 'Title', 'Score', 'Format', 'Episodes', 'Status']
                    st.dataframe(
                        formatted_df,
                        hide_index=True,
                        column_config={
                            "Score": st.column_config.ProgressColumn(
                                "Rating",
                                help="Anime rating out of 10",
                                format="%.2f",
                                min_value=0,
                                max_value=10
                            ),
                            "Rank": st.column_config.NumberColumn(
                                "Rank",
                                help="Current ranking position"
                            )
                        }
                    )
                    
                    # Create two columns for visualizations
                    viz_col1, viz_col2 = st.columns(2)
                    
                    with viz_col1:
                        # Score distribution
                        fig1 = px.histogram(
                            df,
                            x='score',
                            title='Score Distribution',
                            nbins=20,
                            color_discrete_sequence=['#FF4B4B']
                        )
                        fig1.update_layout(
                            height=chart_height,
                            xaxis_title="Score",
                            yaxis_title="Number of Anime"
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with viz_col2:
                        # Format distribution
                        fig2 = px.pie(
                            df,
                            names='type',
                            title='Format Distribution',
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig2.update_layout(height=chart_height)
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # Add insights section
                    st.subheader("🔍 Key Insights", divider="gray")
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        avg_score = df['score'].mean()
                        st.metric(
                            "Average Score",
                            f"{avg_score:.2f}",
                            help="Mean score of displayed anime"
                        )
                    
                    with metric_col2:
                        total_entries = len(df)
                        st.metric(
                            "Total Entries",
                            f"{total_entries}",
                            help="Number of anime in current selection"
                        )
                    
                    with metric_col3:
                        most_common_type = df['type'].mode()[0]
                        st.metric(
                            "Most Common Format",
                            most_common_type,
                            help="Most frequent anime format"
                        )
                    
                    # Original scatter plot with improvements
                    st.subheader("📈 Score vs Popularity Analysis", divider="gray")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df['members'],
                        y=df['score'],
                        mode='markers',
                        text=df['title'],
                        hovertemplate="<b>%{text}</b><br>" +
                                    "Score: %{y:.2f}<br>" +
                                    "Members: %{x:,}<br>" +
                                    "<extra></extra>",
                        marker=dict(
                            size=10,
                            color=df['rank'],
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title="Rank")
                        )
                    ))
                    
                    fig.update_layout(
                        title='Correlation between Popularity and Ratings',
                        xaxis_title='Number of Members (Popularity)',
                        yaxis_title='Score',
                        showlegend=False,
                        height=chart_height
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add download capability
                    st.download_button(
                        "📥 Download Rankings Data",
                        df.to_csv(index=False).encode('utf-8'),
                        "top_anime_rankings.csv",
                        "text/csv",
                        help="Download the current rankings as a CSV file"
                    )
                    
    except Exception as e:
        st.error(f"An error occurred while fetching top anime: {str(e)}")
        logger.error(f"Error in Top Anime view: {str(e)}")

# =====================================================================
# COMPARE ANIME VIEW - Compare two anime side by side
# =====================================================================
else:  # Compare Anime
    logger.info("Accessing Compare Anime view")
    
    st.header("⚖️ Anime Comparison Engine", divider="rainbow")
    st.caption("Analyze key differences between two anime to make informed viewing decisions")
    
    # Help guide for comparison feature
    with st.expander("💡 How to use comparison"):
        st.markdown("""
        Compare two anime to:
        - See which better matches your preferences
        - Understand time investment required
        - Compare ratings and popularity
        - Find common themes and genres
        - Make informed watching decisions
        """)
    
    # Initialize session state if needed
    if 'anime1' not in st.session_state:
        st.session_state.anime1 = None
    if 'anime2' not in st.session_state:
        st.session_state.anime2 = None
    
    # Function to get anime suggestions
    @st.cache_data(ttl=300)  # Cache suggestions for 5 minutes
    def get_anime_suggestions(search_term):
        if not search_term:
            return []
        try:
            params = {'q': search_term, 'sfw': 'true', 'limit': 5}
            results = rate_limited_request(f"{JIKAN_API_URL}/anime", params=params)
            if results.get('data'):
                return [(
                    anime['title'],
                    anime.get('title_english', ''),
                    anime.get('title_japanese', ''),
                    anime.get('images', {}).get('jpg', {}).get('small_image_url', ''),
                    str(anime.get('mal_id', ''))
                ) for anime in results['data']]
            return []
        except Exception as e:
            logger.error(f"Error fetching suggestions: {str(e)}")
            return []

    # Callback functions for selection
    def select_anime1(title):
        st.session_state.anime1 = title
        
    def select_anime2(title):
        st.session_state.anime2 = title

    # Create two columns for entering anime titles
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### First Anime")
        # Show current selection if exists
        if st.session_state.anime1:
            st.success(f"Selected: {st.session_state.anime1}")
            if st.button("Clear Selection", key="clear1"):
                st.session_state.anime1 = None
                st.rerun()
        
        anime1_search = st.text_input(
            "Search first anime",
            placeholder="Type to search anime...",
            key="search1"
        )
        
        # Show suggestions as the user types
        if anime1_search:
            suggestions1 = get_anime_suggestions(anime1_search)
            if suggestions1:
                st.write("Select an anime:")
                for idx, (title, eng, jp, img, mal_id) in enumerate(suggestions1):
                    with st.container():
                        cols = st.columns([1, 4])
                        with cols[0]:
                            if img:
                                st.image(img, width=50)
                        with cols[1]:
                            if st.button(
                                title,
                                key=f"btn1_{mal_id}_{idx}",
                                help=f"English: {eng if eng else 'N/A'}\nJapanese: {jp if jp else 'N/A'}"
                            ):
                                select_anime1(title)
                                st.rerun()
            else:
                st.info("No matches found. Try a different search term.")
    
    with col2:
        st.markdown("### Second Anime")
        # Show current selection if exists
        if st.session_state.anime2:
            st.success(f"Selected: {st.session_state.anime2}")
            if st.button("Clear Selection", key="clear2"):
                st.session_state.anime2 = None
                st.rerun()
        
        anime2_search = st.text_input(
            "Search second anime",
            placeholder="Type to search anime...",
            key="search2"
        )
        
        # Show suggestions as the user types
        if anime2_search:
            suggestions2 = get_anime_suggestions(anime2_search)
            if suggestions2:
                st.write("Select an anime:")
                for idx, (title, eng, jp, img, mal_id) in enumerate(suggestions2):
                    with st.container():
                        cols = st.columns([1, 4])
                        with cols[0]:
                            if img:
                                st.image(img, width=50)
                        with cols[1]:
                            if st.button(
                                title,
                                key=f"btn2_{mal_id}_{idx}",
                                help=f"English: {eng if eng else 'N/A'}\nJapanese: {jp if jp else 'N/A'}"
                            ):
                                select_anime2(title)
                                st.rerun()
            else:
                st.info("No matches found. Try a different search term.")
    
    # Execute comparison when both anime titles are selected
    if st.session_state.anime1 and st.session_state.anime2:
        anime1 = st.session_state.anime1
        anime2 = st.session_state.anime2
        try:
            with st.spinner("Analyzing comparison..."):
                logger.info(f"Comparing anime: {anime1} vs {anime2}")
                
                # Get data for both anime using the API
                params1 = {'q': anime1, 'sfw': 'true', 'limit': 1}
                params2 = {'q': anime2, 'sfw': 'true', 'limit': 1}
                
                results1 = rate_limited_request(f"{JIKAN_API_URL}/anime", params=params1)
                results2 = rate_limited_request(f"{JIKAN_API_URL}/anime", params=params2)
                
                # Check if both anime were found
                if not (results1.get('data') and results2.get('data')):
                    st.warning("One or both anime not found. Please check the titles.")
                    logger.warning(f"Anime not found: {anime1} and/or {anime2}")
                else:
                    # Extract the data for each anime
                    a1 = results1['data'][0]
                    a2 = results2['data'][0]
                    
                    # Section 1: Visual Overview
                    st.subheader("📊 Head-to-Head Overview", divider="gray")
                    overview_col1, overview_col2 = st.columns(2)
                    
                    with overview_col1:
                        st.image(a1['images']['jpg']['image_url'], width=200)
                        st.markdown(f"### {a1['title']}")
                        st.caption(f"{a1.get('synopsis', 'No synopsis available.')[:200]}...")
                    
                    with overview_col2:
                        st.image(a2['images']['jpg']['image_url'], width=200)
                        st.markdown(f"### {a2['title']}")
                        st.caption(f"{a2.get('synopsis', 'No synopsis available.')[:200]}...")
                    
                    # Section 2: Key Metrics Comparison
                    st.subheader("📈 Statistical Analysis", divider="gray")
                    
                    # Compare key metrics with progress bars
                    metrics = {
                        'Score': (a1.get('score', 0), a2.get('score', 0), '⭐'),
                        'Popularity': (a1.get('members', 0), a2.get('members', 0), '👥'),
                        'Episodes': (a1.get('episodes', 0), a2.get('episodes', 0), '📺')
                    }
                    
                    for metric, (val1, val2, icon) in metrics.items():
                        st.markdown(f"**{icon} {metric}**")
                        col1, col2 = st.columns(2)
                        
                        max_val = max(val1, val2) if isinstance(val1, (int, float)) and isinstance(val2, (int, float)) else 1
                        
                        with col1:
                            if isinstance(val1, (int, float)):
                                st.progress(val1 / (max_val if max_val > 0 else 1))
                            st.caption(f"{a1['title']}: {val1:,}")
                        
                        with col2:
                            if isinstance(val2, (int, float)):
                                st.progress(val2 / (max_val if max_val > 0 else 1))
                            st.caption(f"{a2['title']}: {val2:,}")
                    
                    # Section 3: Content Analysis
                    st.subheader("📖 Content Breakdown", divider="gray")
                    content_col1, content_col2 = st.columns(2)
                    
                    with content_col1:
                        with st.expander(f"{a1['title']} Details"):
                            st.write("**Type:** ", a1.get('type', 'Unknown'))
                            st.write("**Status:** ", a1.get('status', 'Unknown'))
                            st.write("**Aired:** ", a1.get('aired', {}).get('string', 'Unknown'))
                            st.write("**Genres:** ", ', '.join(g['name'] for g in a1.get('genres', [])))
                            st.write("**Studios:** ", ', '.join(s['name'] for s in a1.get('studios', [])))
                    
                    with content_col2:
                        with st.expander(f"{a2['title']} Details"):
                            st.write("**Type:** ", a2.get('type', 'Unknown'))
                            st.write("**Status:** ", a2.get('status', 'Unknown'))
                            st.write("**Aired:** ", a2.get('aired', {}).get('string', 'Unknown'))
                            st.write("**Genres:** ", ', '.join(g['name'] for g in a2.get('genres', [])))
                            st.write("**Studios:** ", ', '.join(s['name'] for s in a2.get('studios', [])))
                    
                    # Section 4: Quick Insights
                    st.subheader("🎯 Quick Insights", divider="gray")
                    
                    # Score comparison
                    score1, score2 = a1.get('score', 0), a2.get('score', 0)
                    if score1 > score2:
                        st.success(f"🏆 **Higher Rated:** {a1['title']} ({score1} vs {score2})")
                    elif score2 > score1:
                        st.success(f"🏆 **Higher Rated:** {a2['title']} ({score2} vs {score1})")
                    
                    # Genre analysis
                    genres1 = {g['name'] for g in a1.get('genres', [])}
                    genres2 = {g['name'] for g in a2.get('genres', [])}
                    common_genres = genres1 & genres2
                    if common_genres:
                        st.info(f"🎭 **Shared Genres:** {', '.join(common_genres)}")
                    
                    # Time investment analysis
                    if isinstance(a1.get('episodes'), int) and isinstance(a2.get('episodes'), int):
                        avg_episode_length = 23  # minutes
                        time1 = a1['episodes'] * avg_episode_length
                        time2 = a2['episodes'] * avg_episode_length
                        st.warning(
                            f"⏱️ **Time Investment:**\n"
                            f"- {a1['title']}: ~{time1//60}h {time1%60}m\n"
                            f"- {a2['title']}: ~{time2//60}h {time2%60}m"
                        )
                    
                    # Download comparison data
                    comparison_data = pd.DataFrame({
                        'Metric': ['Score', 'Episodes', 'Members', 'Type', 'Status'],
                        a1['title']: [
                            a1.get('score', 'N/A'),
                            a1.get('episodes', 'N/A'),
                            a1.get('members', 'N/A'),
                            a1.get('type', 'N/A'),
                            a1.get('status', 'N/A')
                        ],
                        a2['title']: [
                            a2.get('score', 'N/A'),
                            a2.get('episodes', 'N/A'),
                            a2.get('members', 'N/A'),
                            a2.get('type', 'N/A'),
                            a2.get('status', 'N/A')
                        ]
                    })
                    
                    st.download_button(
                        "📥 Download Comparison Data",
                        comparison_data.to_csv().encode('utf-8'),
                        "anime_comparison.csv",
                        "text/csv",
                        help="Download detailed comparison metrics as CSV"
                    )
                    
        except Exception as e:
            st.error(f"An error occurred while comparing anime: {str(e)}")
            logger.error(f"Error in Compare Anime view: {str(e)}")

# =====================================================================
# Optional "About" section in the sidebar
# =====================================================================
# Component 10: Checkbox for showing/hiding the About section
if st.sidebar.checkbox("Show About"):
    st.sidebar.markdown("""
    ## About
    This dashboard allows you to:
    - Search and explore anime
    - View top anime rankings
    - Compare different anime
    
    Data source: [MyAnimeList](https://myanimelist.net/) via [Jikan API v4](https://docs.api.jikan.moe/)
    """) 