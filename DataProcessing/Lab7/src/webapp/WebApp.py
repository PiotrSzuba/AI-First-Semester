import time
import threading
import pandas as pd
import altair as alt
import streamlit as st
from typing import List, Tuple
from src.data.Context import Context
from src.types.Classifier import Classifier
from src.webapp.Styles import sticky_css

subreddit_input_thread = None

class WebApp:
    def __init__(self) -> None:
        self._color_scheme = {
            "anger": "red",
            "fear": "purple",
            "joy": "lime",
            "sadness": "orange",
            "love": "white",
            "surprise": "cyan",
        }
    
    def run(self):
        st.set_page_config(layout="wide")
        self._subreddit_input()
        cached_subreddits = Context.get_cached_subreddits()
        subreddit_df, selected_subreddit = self._select_box(cached_subreddits)
        st.title(f"Emotions in {selected_subreddit} Subreddit")
        
        st.progress(Context.get_progress(selected_subreddit))
        
        col1, col2 = st.columns(2)
        
        with col1:
            col11, col12 = st.columns(2)
            with col11:
                max_value = st.number_input("Enter max hours:", min_value=0, step=1, value=48)
            with col12:
                step = st.number_input("Enter step:", min_value=0, max_value=max_value, step=1, value=24)
            cols = st.columns(len(Classifier.emotions))
            
            checked_emotions: List[str] = []
            for col, emotion in zip(cols, Classifier.emotions):
                with col:
                    checkbox_value = st.checkbox(emotion, value=True, key=emotion)
                    if not checkbox_value:
                        continue
                    checked_emotions.append(emotion)
        
        with col2:
            average_from_n_days = self._average_from_n_day_changer(max_value, step)
        
        self._plot_emotions(subreddit_df, average_from_n_days, checked_emotions)
        self._plot_average_emotions(subreddit_df, checked_emotions)
        
        col1, col2 = st.columns(2)
        with col1:
            
            n_top = st.number_input("Show top:", min_value=1, max_value=30, step=1, value=15)
        with col2:
            min_comments = st.number_input("Min comments to analyze:", min_value=1, max_value=10, step=1, value=5)
            
        for emotion in checked_emotions:
            self._plot_top_users_by_emotion(selected_subreddit, emotion, n_top, min_comments)
        time.sleep(2)
        st.experimental_rerun()
        
    def _select_box(self, cached_subreddits: List[str]):
        st.markdown(f"<style>{sticky_css}</style>", unsafe_allow_html=True)
        st.markdown("<div class='sticky' id='selectbox-container'></div>", unsafe_allow_html=True)
        selected_subreddit = st.selectbox("Select a saved subreddit:", cached_subreddits, key="selectbox-container")
        subreddit_df = Context.get_subreddit(selected_subreddit)
        
        return subreddit_df, selected_subreddit
    
    def _average_from_n_day_changer(self, max_value=240, step=24) -> int:
        average_from_n_days = st.slider(f"Average from days", label_visibility="hidden", min_value=0, max_value=max_value, step=step, value=step)
        st.text(f"Average from {average_from_n_days} Hours:")
        
        return int(average_from_n_days)
    
    def _subreddit_input(self):
        global subreddit_input_thread
        
        keyword = st.text_input("Enter new subreddit:")
        
        if keyword and keyword not in Context.get_cached_subreddits():      
            if subreddit_input_thread is None or not subreddit_input_thread.is_alive():
                subreddit_input_thread = threading.Thread(target=Context.get_subreddit, args=(keyword,))
                subreddit_input_thread.start()
        
        
    def _plot_emotions(self, data: pd.DataFrame, average_from_n: int, emotions: List[str]):
        if data is None:
            return
        df = Context.get_average_data(data, average_from_n if average_from_n > 0 else 1, emotions)
        chart = self._create_emotion_chart(df)
        st.altair_chart(chart, use_container_width=True)
        
    def _create_emotion_chart(self, df: pd.DataFrame) -> alt.Chart:
        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x="date:T",
                y=alt.Y("value:Q", scale=alt.Scale(domain=[0, 1])),
                color=alt.Color("emotion:N", legend=alt.Legend(title="Emotions"), scale=alt.Scale(domain=list(self._color_scheme.keys()), range=list(self._color_scheme.values()))),
                tooltip=["date", "emotion", "value"],
            )
            .properties(title="Emotions over time")
        )

        return chart
    
    def _plot_average_emotions(self, data: pd.DataFrame, emotions: List[str]):
        if data is None:
            return
        chart = self._create_average_emotions_chart(Context.get_overall_average_data(data, emotions))
        st.altair_chart(chart, use_container_width=True)
    
    def _create_average_emotions_chart(self, df: pd.DataFrame) -> alt.Chart:
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("emotion:N", title="Emotions", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("value:Q", title="Average Value", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("emotion:N", scale=alt.Scale(domain=list(self._color_scheme.keys()), range=list(self._color_scheme.values())), legend=None),
            tooltip=["emotion", "value"],
        ).properties(title="Average Emotions")

        return chart
    
    def _plot_top_users_by_emotion(self, subreddit_name: str, emotion: str, n_top: int = 15, min_comments: int = 3):
        chart = self._create_top_users_by_emotion_chart(Context.get_top_users_by_emotion(subreddit_name, emotion, n_top, min_comments), emotion)
        st.altair_chart(chart, use_container_width=True)
    
    def _create_top_users_by_emotion_chart(self, df: pd.DataFrame, emotion: str) -> alt.Chart:
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("username:N", title="users", axis=alt.Axis(labelAngle=0), sort=alt.EncodingSortField(field=emotion, order='descending')),
            y=alt.Y(f"{emotion}:Q", title=f"Average {emotion}", scale=alt.Scale(domain=[0, 1])),
            tooltip=["username", emotion],
        ).properties(title=f"Top {emotion} users")

        return chart