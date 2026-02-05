import streamlit as st


def render_title(title: str, tooltip: str, heading: str = "###") -> None:
    label = (
        f"{heading} {title} "
        f"<span class=\"info-tooltip\" data-tooltip=\"{tooltip}\">ⓘ</span>"
    )
    st.markdown(label, unsafe_allow_html=True)


def metric_with_info(
    label: str,
    tooltip: str,
    value: str,
    delta: str | None = None,
    delta_color: str = "normal",
) -> None:
    st.markdown(
        f"**{label}** <span class=\"info-tooltip\" data-tooltip=\"{tooltip}\">ⓘ</span>",
        unsafe_allow_html=True,
    )
    if delta is None:
        st.metric(label=" ", value=value)
    else:
        st.metric(label=" ", value=value, delta=delta, delta_color=delta_color)
