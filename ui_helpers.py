import os
import streamlit as st

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#eef0f6",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
)


def load_css(base_dir, filename="style.css"):
    with open(os.path.join(base_dir, filename), encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


def metric_row(metrics):
    for col, metric in zip(st.columns(len(metrics)), metrics):
        label, value, *extra = metric
        col.metric(label, value, **(extra[0] if extra else {}))


def chart(fig):
    st.plotly_chart(fig, use_container_width=True)


def download_reports(data, rows):
    for label, key, filename in rows:
        st.download_button(label, data[key].to_csv(index=False), filename, "text/csv", use_container_width=True)

