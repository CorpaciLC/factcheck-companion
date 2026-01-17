"""Fact-Check Companion - Public Dashboard

Shows outputs and the signals behind them (fact-check matches, trusted coverage,
creator-pattern flags).

Optimized for top performers: high signal-to-noise, explicit confidence, and an
auditable trail of sources.
"""
from __future__ import annotations


import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import random
from typing import List, Dict, Optional


# Supabase is optional - dashboard works with mock data if not installed
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    create_client = None


# Page config
st.set_page_config(
    page_title="Fact-Check Companion - Public Log",
    page_icon="🔍",
    layout="wide",
)


# Supabase connection
@st.cache_resource
def get_supabase():
    if not SUPABASE_AVAILABLE:
        return None
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)




@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_queries(limit: int = 500):
    """Fetch recent queries from Supabase."""
    client = get_supabase()
    if not client:
        return []


    try:
        response = client.table("queries") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return []




def generate_mock_data() -> list[dict]:
    """Generate realistic mock data for demo purposes."""
    mock_videos = [
        {
            "platform": "youtube",
            "video_title": "URGENT: Major Earthquake Predicted for California Next Week!",
            "video_creator": "DoomsdayPrepper2024",
            "video_url": "https://youtube.com/watch?v=fake1",
            "claim_extracted": "A massive 9.0 earthquake will hit California within the next 7 days based on secret government data",
            "confidence": "high",
            "explanation": "I looked into this video. The claim that a major earthquake is predicted for next week is not supported by any scientific evidence. The USGS and California Geological Survey have not issued any such warnings. Earthquakes cannot be predicted with this level of precision. The channel 'DoomsdayPrepper2024' has a history of posting alarming predictions that haven't come true. While California is earthquake-prone, there's no imminent threat beyond the usual background risk.",
            "sources": ["https://www.usgs.gov/faqs/can-you-predict-earthquakes", "https://www.reuters.com/fact-check/"],
            "channel_is_suspect": True,
            "fact_checks_found": 2,
            "search_results_found": 3,
        },
        {
            "platform": "youtube",
            "video_title": "This common food is KILLING you slowly - doctors exposed!",
            "video_creator": "HealthTruthRevealed",
            "video_url": "https://youtube.com/watch?v=fake2",
            "claim_extracted": "Eating bread causes immediate organ damage and doctors are hiding this",
            "confidence": "high",
            "explanation": "This video makes exaggerated claims about bread being harmful. While some people have gluten sensitivity or celiac disease, bread is a staple food consumed safely by billions. The claim that 'doctors are hiding' health information is a common conspiracy trope. Major health organizations like the WHO and NHS consider whole grain bread part of a healthy diet. The video cherry-picks studies and misrepresents scientific consensus.",
            "sources": ["https://www.nhs.uk/live-well/eat-well/", "https://www.snopes.com/"],
            "channel_is_suspect": True,
            "fact_checks_found": 1,
            "search_results_found": 4,
        },
        {
            "platform": "tiktok",
            "video_title": "You won't believe what they found in the water supply",
            "video_creator": "@conspiracyuncovered",
            "video_url": "https://tiktok.com/@user/video/fake3",
            "claim_extracted": "Government is adding mind control chemicals to tap water",
            "confidence": "high",
            "explanation": "This is a recycled conspiracy theory that has been debunked many times. Water treatment facilities add chlorine for disinfection and fluoride for dental health in many areas - both are well-studied and safe at regulated levels. There is no evidence of 'mind control chemicals.' Water quality reports are public. If you're concerned about your local water, you can request a free water quality report from your municipality.",
            "sources": ["https://www.epa.gov/ground-water-and-drinking-water", "https://www.snopes.com/fact-check/fluoride/"],
            "channel_is_suspect": True,
            "fact_checks_found": 3,
            "search_results_found": 2,
        },
        {
            "platform": "youtube",
            "video_title": "New study shows coffee prevents heart disease",
            "video_creator": "ScienceDaily",
            "video_url": "https://youtube.com/watch?v=fake4",
            "claim_extracted": "Drinking 3-4 cups of coffee daily reduces heart disease risk by 15%",
            "confidence": "medium",
            "explanation": "This claim is partially accurate but oversimplified. A 2022 study in the European Journal of Preventive Cardiology did find an association between moderate coffee consumption and reduced cardiovascular risk. However, correlation doesn't equal causation, and individual responses to coffee vary. The video presents the finding accurately but doesn't mention limitations. Moderate coffee consumption is generally considered safe for most adults.",
            "sources": ["https://www.bbc.com/news/health-62655963", "https://academic.oup.com/eurjpc"],
            "channel_is_suspect": False,
            "fact_checks_found": 0,
            "search_results_found": 3,
        },
        {
            "platform": "youtube",
            "video_title": "BREAKING: Banks will collapse Monday morning!",
            "video_creator": "FinancialDoomCast",
            "video_url": "https://youtube.com/watch?v=fake5",
            "claim_extracted": "All major banks will fail this Monday due to hidden debt crisis",
            "confidence": "high",
            "explanation": "This is fear-mongering without credible evidence. Major financial institutions are regulated and stress-tested. The Federal Reserve, FDIC, and financial news outlets (Bloomberg, Reuters, WSJ) have not reported any imminent banking crisis. This channel has made similar predictions before that did not materialize. While economic risks always exist, claims of specific imminent collapse are almost always false.",
            "sources": ["https://www.reuters.com/business/finance/", "https://www.federalreserve.gov/"],
            "channel_is_suspect": True,
            "fact_checks_found": 1,
            "search_results_found": 2,
        },
        {
            "platform": "tiktok",
            "video_title": "This plant cures diabetes naturally",
            "video_creator": "@naturalhealing",
            "video_url": "https://tiktok.com/@user/video/fake6",
            "claim_extracted": "Cinnamon can completely cure type 2 diabetes without medication",
            "confidence": "high",
            "explanation": "This claim is dangerously misleading. While some studies show cinnamon may have modest effects on blood sugar levels, it cannot 'cure' diabetes. Type 2 diabetes is a chronic condition that requires proper medical management. Stopping prescribed medication based on social media advice can lead to serious complications. Always consult your doctor before making changes to diabetes treatment.",
            "sources": ["https://www.diabetes.org/", "https://www.snopes.com/fact-check/cinnamon-diabetes/"],
            "channel_is_suspect": True,
            "fact_checks_found": 2,
            "search_results_found": 3,
        },
        {
            "platform": "youtube",
            "video_title": "NASA confirms asteroid heading for Earth",
            "video_creator": "SpaceNewsNetwork",
            "video_url": "https://youtube.com/watch?v=fake7",
            "claim_extracted": "Large asteroid will impact Earth in 2025",
            "confidence": "high",
            "explanation": "This is a misrepresentation. NASA does track near-Earth objects and publishes this data publicly. There is no known asteroid on a collision course with Earth for the foreseeable future. NASA's Planetary Defense Coordination Office would alert the public of any genuine threat. The video likely references a routine asteroid flyby (which happen regularly at safe distances) and exaggerates it for views.",
            "sources": ["https://www.nasa.gov/planetarydefense", "https://cneos.jpl.nasa.gov/"],
            "channel_is_suspect": False,
            "fact_checks_found": 1,
            "search_results_found": 4,
        },
        {
            "platform": "youtube",
            "video_title": "The truth about 5G they don't want you to know",
            "video_creator": "TechConspiracy",
            "video_url": "https://youtube.com/watch?v=fake8",
            "claim_extracted": "5G towers cause cancer and COVID-19",
            "confidence": "high",
            "explanation": "These claims have been thoroughly debunked. 5G uses non-ionizing radiation, which does not damage DNA or cause cancer - this is established physics. COVID-19 is caused by a virus (SARS-CoV-2), not radio waves. Multiple studies and health organizations (WHO, FDA, ICNIRP) confirm 5G is safe within regulated limits. The video relies on misunderstanding of electromagnetic radiation and viral transmission.",
            "sources": ["https://www.who.int/news-room/q-a-detail/5g-mobile-networks-and-health", "https://www.reuters.com/article/uk-factcheck-5g-covid/"],
            "channel_is_suspect": True,
            "fact_checks_found": 5,
            "search_results_found": 3,
        },
        {
            "platform": "tiktok",
            "video_title": "Secret cure for cancer hidden by pharma",
            "video_creator": "@bigpharmaexposed",
            "video_url": "https://tiktok.com/@user/video/fake9",
            "claim_extracted": "Pharmaceutical companies are hiding a cancer cure for profit",
            "confidence": "high",
            "explanation": "This is a harmful conspiracy theory. Cancer is not one disease but hundreds, each requiring different treatments. Scientists worldwide (including in countries with public healthcare) research cancer treatments - a 'hidden cure' would be impossible to suppress globally. New treatments are regularly developed and made available. This narrative discourages people from seeking proven medical care. Please consult oncologists for cancer treatment.",
            "sources": ["https://www.cancer.org/", "https://www.snopes.com/fact-check/exposed-exposed/"],
            "channel_is_suspect": True,
            "fact_checks_found": 3,
            "search_results_found": 2,
        },
        {
            "platform": "youtube",
            "video_title": "Climate change update: New IPCC report findings",
            "video_creator": "ClimateScience",
            "video_url": "https://youtube.com/watch?v=fake10",
            "claim_extracted": "Global temperatures have risen 1.1C since pre-industrial times",
            "confidence": "high",
            "explanation": "This claim is accurate and well-sourced. The IPCC's Sixth Assessment Report confirms global surface temperature has increased by approximately 1.1°C compared to 1850-1900. This is based on multiple independent datasets and is the scientific consensus. The video accurately represents the current state of climate science.",
            "sources": ["https://www.ipcc.ch/report/ar6/wg1/", "https://www.bbc.com/news/science-environment-58130705"],
            "channel_is_suspect": False,
            "fact_checks_found": 0,
            "search_results_found": 5,
        },
    ]


    # Generate timestamps over the past 30 days
    now = datetime.now()
    result = []


    for i, video in enumerate(mock_videos):
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        created_at = now - timedelta(days=days_ago, hours=hours_ago)


        result.append({
            "id": f"mock-{i+1}",
            "created_at": created_at.isoformat(),
            **video
        })


    # Sort by created_at descending
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return result




def main():
    # Header
    st.title("🔍 Fact-Check Companion")
    st.markdown("""
    ### Public Query Log


    This dashboard shows all videos that have been fact-checked through our WhatsApp bot.


    **Privacy:** No phone numbers or user identifiers are stored. Only the video information
    and our analysis is recorded.


    ---
    """)


    # Check Supabase connection and fetch data
    client = get_supabase()
    using_mock_data = False


    if client:
        queries = fetch_queries()
        if not queries:
            st.info("No queries recorded yet. Send a video to the WhatsApp bot to see it appear here!")
            st.markdown("---")
            st.markdown("**Demo Mode:** Showing sample data below to demonstrate the dashboard.")
            queries = generate_mock_data()
            using_mock_data = True
    else:
        st.info("📋 **Demo Mode** - Showing sample data. Connect Supabase for live data.")
        queries = generate_mock_data()
        using_mock_data = True


    if using_mock_data:
        st.caption("ℹ️ This is sample data for demonstration. Real queries will appear once the bot is active.")


    # Convert to DataFrame
    df = pd.DataFrame(queries)


    # Parse timestamps
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["date"] = df["created_at"].dt.date


    # Sidebar filters
    st.sidebar.header("Filters")


    # Platform filter
    platforms = ["All"] + list(df["platform"].unique())
    selected_platform = st.sidebar.selectbox("Platform", platforms)


    # Confidence filter
    confidences = ["All"] + list(df["confidence"].unique())
    selected_confidence = st.sidebar.selectbox("Confidence Level", confidences)


    # Channel suspect filter
    show_suspect_only = st.sidebar.checkbox("Show only suspicious channels")


    # Search
    search_query = st.sidebar.text_input("Search video titles")


    # Apply filters
    filtered_df = df.copy()


    if selected_platform != "All":
        filtered_df = filtered_df[filtered_df["platform"] == selected_platform]


    if selected_confidence != "All":
        filtered_df = filtered_df[filtered_df["confidence"] == selected_confidence]


    if show_suspect_only:
        filtered_df = filtered_df[filtered_df["channel_is_suspect"] == True]


    if search_query:
        mask = (
            filtered_df["video_title"].str.contains(search_query, case=False, na=False) |
            filtered_df["claim_extracted"].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[mask]


    # Stats row
    col1, col2, col3, col4 = st.columns(4)


    with col1:
        st.metric("Total Queries", len(df))


    with col2:
        youtube_count = len(df[df["platform"] == "youtube"])
        st.metric("YouTube Videos", youtube_count)


    with col3:
        tiktok_count = len(df[df["platform"] == "tiktok"])
        st.metric("TikTok Videos", tiktok_count)


    with col4:
        high_confidence = len(df[df["confidence"] == "high"])
        pct = (high_confidence / len(df) * 100) if len(df) > 0 else 0
        st.metric("High Confidence", f"{pct:.0f}%")


    st.markdown("---")


    # Display results
    st.subheader(f"Showing {len(filtered_df)} queries")


    for idx, row in filtered_df.iterrows():
        with st.expander(f"📹 {row.get('video_title', 'Unknown Title')[:80]}..."):
            col1, col2 = st.columns([2, 1])


            with col1:
                st.markdown(f"**Platform:** {row.get('platform', 'unknown').upper()}")
                st.markdown(f"**Creator:** {row.get('video_creator', 'Unknown')}")
                st.markdown(f"**Video URL:** [{row.get('video_url', '')}]({row.get('video_url', '')})")


                if row.get("channel_is_suspect"):
                    st.warning("⚠️ This channel frequently posts alarmist content")


            with col2:
                confidence = row.get("confidence", "unknown")
                if confidence == "high":
                    st.success("✅ High Confidence")
                elif confidence == "medium":
                    st.info("📊 Medium Confidence")
                else:
                    st.warning("❓ Low Confidence")


                st.markdown(f"**Fact-checks found:** {row.get('fact_checks_found', 0)}")
                st.markdown(f"**News articles found:** {row.get('search_results_found', 0)}")


            st.markdown("---")
            st.markdown("**Our Explanation:**")
            st.markdown(row.get("explanation", "No explanation available"))


            sources = row.get("sources", [])
            if sources:
                st.markdown("**Sources:**")
                for source in sources[:5]:
                    st.markdown(f"- [{source}]({source})")


            if "created_at" in row:
                st.caption(f"Checked on: {row['created_at']}")


    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Built with care for families dealing with misinformation.</p>
        <p>This bot doesn't store any personal information about users.</p>
    </div>
    """, unsafe_allow_html=True)




if __name__ == "__main__":
    main()





