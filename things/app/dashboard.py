"""
Public Fact-Check Dashboard


A Streamlit app that shows all fact-check queries.
Deploy to Streamlit Cloud for free public hosting.
"""


import streamlit as st
from supabase import create_client
from datetime import datetime
import os


# Page config
st.set_page_config(
    page_title="Fact-Check Companion Dashboard",
    page_icon="🔍",
    layout="wide"
)


# Get Supabase credentials from environment or Streamlit secrets
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY", "")




@st.cache_resource
def get_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)




def get_queries(limit=100):
    client = get_client()
    if not client:
        return []
    try:
        response = client.table("queries") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return response.data or []
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return []




def get_stats(queries):
    total = len(queries)
    if total == 0:
        return {}


    platforms = {}
    confidences = {}
    suspect_count = 0


    for q in queries:
        p = q.get("platform", "unknown")
        c = q.get("confidence", "unknown")
        platforms[p] = platforms.get(p, 0) + 1
        confidences[c] = confidences.get(c, 0) + 1
        if q.get("channel_is_suspect"):
            suspect_count += 1


    return {
        "total": total,
        "platforms": platforms,
        "confidences": confidences,
        "suspect_channels": suspect_count
    }




# Header
st.title("🔍 Fact-Check Companion")
st.markdown("*Helping families debunk misleading videos*")
st.divider()


# Check connection
if not SUPABASE_URL or not SUPABASE_KEY:
    st.warning("⚠️ Database not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
    st.stop()


# Fetch data
queries = get_queries(100)
stats = get_stats(queries)


# Stats row
if stats:
    col1, col2, col3, col4 = st.columns(4)


    with col1:
        st.metric("Total Checks", stats["total"])


    with col2:
        high = stats["confidences"].get("high", 0)
        st.metric("High Confidence", high)


    with col3:
        yt = stats["platforms"].get("youtube", 0)
        tt = stats["platforms"].get("tiktok", 0)
        st.metric("YouTube / TikTok", f"{yt} / {tt}")


    with col4:
        st.metric("Suspect Channels", stats["suspect_channels"])


st.divider()


# Recent queries
st.subheader("📋 Recent Fact-Checks")


if not queries:
    st.info("No queries yet. Send a video link to the WhatsApp bot to get started!")
else:
    for q in queries:
        with st.expander(f"**{q.get('video_title', 'Unknown')}** — {q.get('confidence', '?').upper()} confidence"):
            col1, col2 = st.columns([2, 1])


            with col1:
                st.markdown(f"**Platform:** {q.get('platform', 'unknown').title()}")
                st.markdown(f"**Creator:** {q.get('video_creator', 'Unknown')}")
                st.markdown(f"**URL:** [{q.get('video_url', '')}]({q.get('video_url', '')})")


                if q.get("channel_is_suspect"):
                    st.warning("⚠️ This channel frequently posts alarmist content")


                st.markdown("---")
                st.markdown("**Explanation sent to user:**")
                st.markdown(q.get("explanation", "N/A"))


            with col2:
                st.markdown(f"**Confidence:** {q.get('confidence', 'unknown')}")
                st.markdown(f"**Fact-checks found:** {q.get('fact_checks_found', 0)}")
                st.markdown(f"**News results:** {q.get('search_results_found', 0)}")


                sources = q.get("sources", [])
                if sources:
                    st.markdown("**Sources:**")
                    for src in sources[:5]:
                        st.markdown(f"- [{src[:50]}...]({src})")


                created = q.get("created_at", "")
                if created:
                    st.markdown(f"**Checked:** {created[:16]}")


# Footer
st.divider()
st.markdown("*Built for the Promptless Products Hackathon*")
st.markdown("*Privacy: No user phone numbers or identifiers are stored*")





