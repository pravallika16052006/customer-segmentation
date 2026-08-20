# SegMenAI Frontend Fix

## Fixed
- Moved global CSS injection from `st.markdown(..., unsafe_allow_html=True)` to `st.html(...)`.
- Moved page-specific CSS from Markdown to `st.html(...)`.
- Removed a `<style>` block that was embedded inside an HTML fragment rendered by the Markdown helper.
- Added a dedicated responsive class for the Segment Analysis summary grid.
- Kept the custom sidebar navigation using `st.navigation(position="hidden")` + `st.page_link(...)`.

## Run
From the project root:

```bash
streamlit run frontend/streamlit_app.py
```
