import streamlit as st
from config.settings import get_settings
from core.session import init
from services.turso import Repos
from ui.layout import shell
from ui.pages import dashboard, projects, workspace, sources, research, ideas, hooks, script, reviews, voice_dna, history
from ui.pages import settings as settings_page

init()
settings = get_settings()
repo = Repos()
page = shell()

if page == 'Dashboard': dashboard.render(repo, settings)
elif page == 'Projects': projects.render(repo, settings)
elif page == 'Create / Workspace': workspace.render(repo, settings)
elif page == 'Sources & PDF': sources.render(repo, settings)
elif page == 'Research': research.render(repo, settings)
elif page == 'Voice DNA': voice_dna.render(repo, settings)
elif page == 'History': history.render(repo, settings)
elif page == 'Settings': settings_page.render(repo, settings)
