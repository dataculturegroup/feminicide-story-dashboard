import streamlit as st

import dashboard.database.alerts_db as alerts
import dashboard.database.processor_db as processor_db
import dashboard.projects as projects
from dashboard import graph_functions as helper

# Projects
st.sidebar.title("Projects")
list_of_projects = projects.load_project_list(
    force_reload=True, download_if_missing=True
)

# Sort the list of projects by ID DESC
sorted_list_of_projects = sorted(
    list_of_projects, key=lambda project: project["id"], reverse=True
)

# Create a list of strings with the project ID and title
titles = ["Click Here to Get A Project's Report"] + [
    f"{project['id']} - {project['title']}" for project in sorted_list_of_projects
]

# Display the selectbox with the updated titles
option = st.sidebar.selectbox("Select Project by ID", (titles))

# Get the selected project ID
if option != "Click Here to Get A Project's Report":
    selected_project_id = int(option.split(" - ")[0])
    selected = [p for p in sorted_list_of_projects if p["id"] == selected_project_id][0]

    # Project Attributes
    st.caption("Project Background")
    st.markdown(f"{selected['id']} - {selected['title']}")
    st.markdown("Model : " + str(selected["language_model"]))
    st.divider()

    # Project Statistics
    unposted_above_story_count = processor_db.unposted_above_story_count(selected["id"])
    posted_above_story_count = processor_db.posted_above_story_count(selected["id"])
    below_story_count = processor_db.below_story_count(selected["id"])
    try:
        above_threshold_pct = round(
            (
                100
                * (unposted_above_story_count + posted_above_story_count)
                / below_story_count
            ),
            2,
        )
    except ZeroDivisionError:
        above_threshold_pct = 100


    # Project Statistics
    st.caption("Project Specific Story Statistics")

    # Display metrics
    col1, col2 = st.columns(2)
    col1.metric("Average Above Threshold Stories Percentage", f"{above_threshold_pct}%")
    col2.metric("Unposted Above Threshold Stories", unposted_above_story_count)

    col3, col4 = st.columns(2)
    col3.metric("Above Threshold Stories Posted to Email Alerts Server", posted_above_story_count)
    col4.metric("Below Threshold Stories", below_story_count)


    # Model Scores
    st.subheader("Model Scores")
    st.caption(
        "Model Scores for the Stories that went through the Classifiers, Scores closer"
        " to 1.0 Indicates the Amount of Stories by Significance"
    )
    helper.draw_model_scores(project_id=selected["id"])
    st.divider()

    st.subheader("Above Threshold Stories by Project")
    # project specific stories by posted day
    st.caption("Stories sent to the email alerts server based on the day they were run against the classifiers, "
           "grouped by the data source they originally came from.")
    helper.draw_graph(processor_db.stories_by_posted_day, selected["id"])
    st.divider()
    # History (by discovery date)
    st.subheader("History of the Project")
    st.caption("Stories discovered on each platform based on the guessed date of publication, grouped by the "
           "data source they originally came from.")
    helper.draw_graph(processor_db.stories_by_published_day, selected["id"])
    st.caption("Stories grouped by Platforms based on Discovery Day")
    helper.draw_graph(processor_db.stories_by_processed_day, selected["id"])
    st.caption("Stories based on the date they were run against the classifiers, grouped by whether they were above"
           "threshold for their associated project or not.")
    helper.story_results_graph(selected["id"])
    st.divider()

      
    st.subheader("Latest Stories in the Project")
    st.caption("Recent Above threshold Stories")
    stories_above = processor_db.recent_stories(selected['id'], True)
    helper.latest_stories(stories_above)

    st.caption("Recent Below threshold Stories")
    stories_below = processor_db.recent_stories(selected['id'], False)
    helper.latest_stories(stories_below)
    
    st.divider()
    
    # Add a section for Email-Alerts database visualizations
    st.title("Email-Alerts Database")

    # Total story count in Email-Alerts for the selected project
    total_email_alerts_story_count = alerts.total_story_count(project_id=selected_project_id)

    st.metric(label=f"Total Stories in Email-Alerts for Project {selected_project_id} - {selected['title']}", value=total_email_alerts_story_count)

    #top media sources 
    st.subheader("Top 10 media sources by story count")
    helper.draw_bar_chart_sources(alerts.top_media_sources_by_story_volume_22, project_id=selected["id"])
    st.divider()
        
    # Story Count by Publication Date
    st.subheader("Story Count by Publication Date")
    helper.alerts_draw_graph(alerts.stories_by_publish_date, project_id=selected["id"])
    
    st.divider()

    # Story Count by Creation Date
    st.subheader("Story Count by Creation Date")
    helper.alerts_draw_graph(alerts.stories_by_creation_date, project_id=selected["id"])
    
    st.divider()


