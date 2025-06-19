#!/usr/bin/env python
# src/latest_ai_development/main.py
import sys
from src.crew import NavigationCrew

def run():
  """
  Run the crew.
  """
  inputs = {
    'topic': 'AI Agents'
  }
  NavigationCrew.crew().kickoff(inputs=inputs)