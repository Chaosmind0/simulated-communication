# Simulated Communication

A web-based demo for character skill chat and voice generation.

## Features

- Select a trained character Skill
- Select a trained voice profile
- Chat through a QQ-style web interface
- Generate voice for assistant replies
- Designed for future Unity and Live2D integration

## Architecture

Frontend -> Backend -> Skill Runtime -> LLM
                     -> Voicebox

## Project Structure

frontend/      Web chat UI
backend/       FastAPI backend
skills/        Generated character skills
config/        Skill and voice configuration
audio_cache/   Generated audio cache
docs/          Design documents

## External Dependencies

- colleague-skill: used to generate character skills
- voicebox: used as the local TTS service