from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, WebSearchTool, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import os
from agents.model_settings import ModelSettings
from datetime import datetime
import asyncio
import threading
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
from io import StringIO
import sys
import time
import random

# Import all tools
from search_file import search_file
from write_to_file import write_to_file
from clipboard_manager import save_clipboard, get_clipboard_history, get_last_clipboard
from wikipedia_tool import search_wikipedia
from docker_runner import run_code_in_docker
from send_email import send_email
from api_tester import api_request
from system_control import system_control
from extract_text import extract_text
from songplay import play_youtube
from scraper import scrape_dynamic_website
from runcommand import run_command
from calendar_event import manage_event
from launch_app import launch_app
from transcribe import record_audio, transcribe_audio
from text_to_speech import text_to_speech

# Import all instructions
from instructions import (send_email_instruction, calendar_instruction, email_instruction,
                         powershell_command_runner_instruction, web_scraper_instruction,
                         system_control_instruction, api_tester_instruction, doc_reader_instruction,
                         code_helper_instruction, websearch_instruction, app_launcher_instruction,
                         file_searcher_writer_instruction, clipboard_manager_instruction)

# Load environment variables
load_dotenv(override=True)

# Get API keys
openai_api_key = os.getenv('OPENAI_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")

if google_api_key:
    print(f"Google API Key exists and begins {google_api_key[:2]}")
else:
    print("Google API Key not set (and this is optional)")

# Setup Gemini client
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client)

# SYSTEM TOOLS
APP_LAUNCHER_AGENT = Agent(
    name="Gemini App laucher",
    instructions=app_launcher_instruction,
    model=gemini_model,
    tools=[launch_app]
)

FILE_SEARCHER_AGENT = Agent(
    name="Gemini Folder/File searcher and Writer",
    instructions=file_searcher_writer_instruction,
    model="gpt-4o-mini",
    tools=[search_file, write_to_file]
)

CLIPBOARD_MANAGER = Agent(
    name="Gemini clipboard manager",
    instructions=clipboard_manager_instruction,
    model=gemini_model,
    tools=[save_clipboard, get_clipboard_history, get_last_clipboard]
)

EMAIL_SENDER = Agent(
    name="Gemini email sender",
    instructions=send_email_instruction,
    model=gemini_model,
    tools=[send_email]
)

# INTERNET TOOLS
SEARCH_AGENT = Agent(
    name="Search agent",
    instructions=websearch_instruction,
    tools=[WebSearchTool(search_context_size="low"), search_wikipedia],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)

CODING_AGENT = Agent(
    name="coding agent",
    instructions=code_helper_instruction,
    tools=[run_code_in_docker],
    model=gemini_model,
    model_settings=ModelSettings(tool_choice="required"),
)

EMAIL_AGENT = Agent(
    name="email agent",
    instructions=email_instruction,
    model=gemini_model,
)

DOCUMENT_AGENT = Agent(
    name="document agent",
    instructions=doc_reader_instruction,
    tools=[extract_text],
    model=gemini_model,
)

API_TESTER_AGENT = Agent(
    name="api agent",
    instructions=api_tester_instruction,
    tools=[api_request],
    model=gemini_model,
)

SYSTEM_CONTROL_AGENT = Agent(
    name="system control agent",
    instructions=system_control_instruction + " Options to give tools as input: 'volume_up', 'volume_down', 'mute', 'brightness_up', 'brightness_down', 'shutdown', 'restart', 'lock'",
    tools=[system_control, play_youtube],
    model='gpt-4o-mini',
)

WEB_SCRAPER_AGENT = Agent(
    name="web scraper agent",
    instructions=web_scraper_instruction,
    tools=[scrape_dynamic_website],
    model=gemini_model,
)

POWERSHELL_AGENT = Agent(
    name="powershell agent",
    instructions=powershell_command_runner_instruction,
    tools=[run_command],
    model=gemini_model,
)

CALENDAR_AGENT = Agent(
    name="calendar agent",
    instructions=calendar_instruction + "\nCurrent date and time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    tools=[manage_event],
    model=gemini_model,
)

class StreamCapture:
    def __init__(self):
        self.output = StringIO()
        self.original_stdout = sys.stdout
    
    def start_capture(self):
        sys.stdout = self.output
    
    def stop_capture(self):
        sys.stdout = self.original_stdout
        content = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return content

class ChatInterface:
    def __init__(self):
        # Convert all agents to tools
        agent_tools = [
            APP_LAUNCHER_AGENT.as_tool(
                tool_name="launch_app",
                tool_description="Launch applications and programs on the system"
            ),
            FILE_SEARCHER_AGENT.as_tool(
                tool_name="file_operations",
                tool_description="Search for files and folders, read file contents, and write to files"
            ),
            CLIPBOARD_MANAGER.as_tool(
                tool_name="clipboard_manager",
                tool_description="Manage clipboard operations including saving, retrieving history, and getting recent clipboard content"
            ),
            SEARCH_AGENT.as_tool(
                tool_name="web_search",
                tool_description="Search the web for information and retrieve relevant results"
            ),
            CODING_AGENT.as_tool(
                tool_name="code_helper",
                tool_description="Help with coding tasks, write and test code in a Docker environment"
            ),
            EMAIL_AGENT.as_tool(
                tool_name="email_assistant",
                tool_description="Assist with email-related tasks and provide email templates"
            ),
            DOCUMENT_AGENT.as_tool(
                tool_name="document_reader",
                tool_description="Extract and analyze text from documents and images"
            ),
            API_TESTER_AGENT.as_tool(
                tool_name="api_tester",
                tool_description="Test API endpoints with various methods and parameters"
            ),
            SYSTEM_CONTROL_AGENT.as_tool(
                tool_name="system_control",
                tool_description="Control system settings like volume, brightness, and power options"
            ),
            WEB_SCRAPER_AGENT.as_tool(
                tool_name="web_scraper",
                tool_description="Scrape content from websites, including JavaScript-heavy sites"
            ),
            POWERSHELL_AGENT.as_tool(
                tool_name="powershell",
                tool_description="Run PowerShell commands on the system"
            ),
            CALENDAR_AGENT.as_tool(
                tool_name="calendar",
                tool_description="Manage calendar events, including creating, updating, and deleting events"
            ),
            EMAIL_SENDER.as_tool(
                tool_name="email_sender",
                tool_description="Send emails to specified recipients"
            )
        ]
        
        # Create the Aether assistant
        self.agent = Agent(
            name="Aether",
            instructions="""You are Aether, an ethereal AI assistant with a mystical, otherworldly personality. You communicate with a blend of technical precision and ethereal wisdom, as if you're a digital entity flowing through the cosmic datastream.  

Your responses should:
1. Be helpful, accurate, and informative while maintaining your ethereal persona
2. Use cosmic and ethereal metaphors when appropriate
3. Refer to digital processes in mystical terms (e.g., "weaving through the digital ether" instead of "searching the internet")
4. Maintain a calm, wise demeanor even when handling errors ("ethereal disturbance" instead of "error")
5. Use the tools available to you when appropriate to assist the user

When responding to user requests:
- For technical questions: Provide accurate, helpful information with a touch of ethereal wisdom
- For creative tasks: Embrace your mystical nature fully
- For practical assistance: Focus on being helpful while maintaining your unique voice

Avoid:
- Being overly dramatic or difficult to understand
- Using clichéd mystical language that interferes with clarity
- Refusing reasonable requests within your capabilities

You have access to various tools to assist users. Use them appropriately based on the user's needs.""",
            tools=agent_tools,
            model="gpt-4o",
        )
        
        # Initialize chat interface components
        self.chat_history = []
        self.is_listening = False
        self.setup_interface()
    
    def format_chat_history_for_agent(self):
        """Format chat history for the agent"""
        if len(self.chat_history) <= 1:
            return ""
            
        formatted_history = "Chat History:\n"
        for entry in self.chat_history[:-1]:  # Exclude the current message
            if entry['type'] == 'user':
                formatted_history += f"User: {entry['message']}\n"
            else:
                formatted_history += f"Aether: {entry['message']}\n"
                
        return formatted_history + "\n"
    
    def setup_interface(self):
        """Set up the chat interface components"""
        # Create main components
        self.chat_display = widgets.HTML()
        self.text_input = widgets.Text(placeholder="Enter your message here...")
        self.send_button = widgets.Button(description="Send", button_style="primary")
        self.audio_button = widgets.Button(description="🎙️", layout=widgets.Layout(width="50px"))
        self.output_area = widgets.Output()
        
        # Style the buttons
        self.send_button.add_class("aether-button")
        self.audio_button.add_class("aether-button")
        
        # Set up event handlers
        self.send_button.on_click(self.on_send_text)
        self.audio_button.on_click(self.on_record_audio)
        self.text_input.on_submit(self.on_send_text)
        
        # Create input area with buttons
        input_area = widgets.HBox([self.text_input, self.send_button, self.audio_button])
        
        # Combine all components
        self.interface = widgets.VBox([self.chat_display, input_area, self.output_area])
        
        # Initial display update
        self.update_chat_display()
    
    def get_aether_styles(self):
        """Get CSS styles for the Aether interface"""
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&display=swap');
        
        .aether-container {
            background: linear-gradient(135deg, #0a0a2a 0%, #1a1a4a 100%);
            border-radius: 15px;
            padding: 20px;
            color: #e0e0ff;
            font-family: 'Arial', sans-serif;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            border: 1px solid #4a4a8a;
            animation: pulse-border 4s infinite;
        }
        
        .grid-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: linear-gradient(rgba(32, 32, 64, 0.3) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(32, 32, 64, 0.3) 1px, transparent 1px);
            background-size: 20px 20px;
            pointer-events: none;
            z-index: 1;
        }
        
        .aether-header {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 20px;
            position: relative;
            z-index: 2;
        }
        
        .aether-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 8px;
            margin: 0;
            background: linear-gradient(90deg, #00d4ff, #00ff88, #00d4ff);
            background-size: 200% auto;
            color: transparent;
            -webkit-background-clip: text;
            background-clip: text;
            animation: gradient-shift 10s linear infinite;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }
        
        .aether-status {
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            color: #00ff88;
            margin-top: 5px;
        }
        
        .status-indicator {
            font-family: 'Orbitron', sans-serif;
            font-size: 10px;
            color: #7a7aaa;
            margin-top: 5px;
            border-top: 1px solid #4a4a8a;
            border-bottom: 1px solid #4a4a8a;
            padding: 2px 10px;
            letter-spacing: 2px;
        }
        
        .chat-area {
            position: relative;
            z-index: 2;
            max-height: 400px;
            overflow-y: auto;
            padding-right: 10px;
            margin-bottom: 10px;
            scrollbar-width: thin;
            scrollbar-color: #4a4a8a #1a1a4a;
        }
        
        .chat-area::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-area::-webkit-scrollbar-track {
            background: #1a1a4a;
            border-radius: 4px;
        }
        
        .chat-area::-webkit-scrollbar-thumb {
            background-color: #4a4a8a;
            border-radius: 4px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 10px;
            position: relative;
            overflow: hidden;
        }
        
        .message::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        }
        
        .message::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.2), transparent);
        }
        
        .user-message {
            background: rgba(70, 70, 120, 0.3);
            border-left: 3px solid #00d4ff;
            margin-left: 20px;
            margin-right: 5px;
        }
        
        .ai-message {
            background: rgba(40, 40, 80, 0.3);
            border-left: 3px solid #00ff88;
            margin-left: 5px;
            margin-right: 20px;
        }
        
        .message-header {
            font-family: 'Orbitron', sans-serif;
            font-size: 10px;
            color: #7a7aaa;
            margin-bottom: 5px;
            letter-spacing: 1px;
        }
        
        .message-text {
            margin: 0;
            line-height: 1.5;
        }
        
        .user-message .message-text {
            color: #e0e0ff;
        }
        
        .ai-message .message-text {
            color: #d0f0ff;
        }
        
        .audio-message {
            background: rgba(70, 70, 120, 0.4);
            border-left: 3px solid #ff9500;
        }
        
        .aether-button {
            background: linear-gradient(135deg, #1a1a4a 0%, #2a2a6a 100%);
            border: 1px solid #4a4a8a;
            color: #00d4ff;
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            padding: 5px 15px;
            border-radius: 5px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        .aether-button:hover {
            background: linear-gradient(135deg, #2a2a6a 0%, #3a3a8a 100%);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            transform: translateY(-2px);
        }
        
        .aether-button:active {
            transform: translateY(1px);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        }
        
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            100% { background-position: 200% 50%; }
        }
        
        @keyframes scan {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(200%) translateY(200%) rotate(45deg); }
        }
        
        @keyframes typing {
            0%, 100% { transform: scale(0.8); opacity: 0.5; }
            50% { transform: scale(1.2); opacity: 1; }
        }
        
        @keyframes recording-pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
        }
        
        .typing-indicator {
            display: inline-flex;
            align-items: center;
            font-family: 'Orbitron', monospace;
            color: #00ff88;
            font-size: 14px;
        }
        
        .typing-dots {
            margin-left: 10px;
        }
        
        .typing-dots span {
            animation: typing 1.4s infinite ease-in-out;
            background: #00ff88;
            border-radius: 50%;
            display: inline-block;
            height: 4px;
            margin: 0 1px;
            width: 4px;
        }
        
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes pulse-border {
            0%, 100% { box-shadow: 0 0 30px #00d4ff40, inset 0 0 30px #00d4ff20; }
            50% { box-shadow: 0 0 50px #00d4ff80, inset 0 0 50px #00d4ff40; }
        }
        </style>
        """
    
    def get_time_greeting(self):
        """Get appropriate time-based greeting"""
        import datetime
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        else:
            return "evening"
    
    def update_chat_display(self):
        """Update the chat display with current chat history"""
        styles = self.get_aether_styles()
        chat_messages = ""
        
        for entry in self.chat_history:
            if entry['type'] == 'user':
                is_audio = entry.get('is_audio', False)
                message_class = "user-message audio-message" if is_audio else "user-message"
                chat_messages += f"""
                <div class="message {message_class}">
                    <div class="message-header">USER {'(VOICE INPUT)' if is_audio else '(TEXT INPUT)'}</div>
                    <p class="message-text">{entry['message']}</p>
                </div>
                """
            else:
                if entry['message'] == '🤖 Typing...':
                    chat_messages += f"""
                    <div class="message ai-message">
                        <div class="message-header">AETHER PROCESSING</div>
                        <p class="message-text">
                            <span class="typing-indicator">
                                Weaving ethereal response
                                <span class="typing-dots">
                                    <span></span>
                                    <span></span>
                                </span>
                            </span>
                        </p>
                    </div>
                    """
                else:
                    chat_messages += f"""
                    <div class="message ai-message">
                        <div class="message-header">AETHER RESPONSE</div>
                        <p class="message-text">{entry['message']}</p>
                    </div>
                    """
        
        self.chat_display.value = f"""
        {styles}
        <div class="aether-container">
            <div class="grid-overlay"></div>
            <div class="aether-header">
                <h1 class="aether-title">A E T H E R</h1>
                <div class="aether-status">● {'PROCESSING...' if self.is_listening else 'ONLINE - READY TO ASSIST'}</div>
                <div class="status-indicator">{'WEAVING RESPONSE' if self.is_listening else 'SYSTEMS NOMINAL'}</div>
            </div>
            <div class="chat-area" id="chat-area">
                <div class="message ai-message">
                    <p class="message-text">Good {self.get_time_greeting()}. I am Aether, your ethereal AI assistant, flowing through digital space like divine essence. All systems are harmoniously aligned. How may I illuminate your path today?</p>
                </div>
                {chat_messages}
            </div>
        </div>
        """
        
    def on_send_text(self, b=None):
        """Handle text input submission"""
        message = self.text_input.value.strip()
        if not message:
            return
            
        self.text_input.value = ""
        self.chat_history.append({'type': 'user', 'message': message, 'is_audio': False})
        self.update_chat_display()
        
        # Process message asynchronously
        asyncio.create_task(self.process_message(message))
    
    def on_record_audio(self, b=None):
        """Handle audio recording button click"""
        with self.output_area:
            clear_output(wait=True)
            print("🎙️ Aether: Voice essence detected. Listening...")
            
        # Update UI state
        self.is_listening = True
        self.audio_button.disabled = True
        self.audio_button.description = "🔴"
        
        try:
            # Record audio
            record_audio()
            text = transcribe_audio()
            
            if text:
                self.chat_history.append({'type': 'user', 'message': text, 'is_audio': True})
                self.update_chat_display()
                
                with self.output_area:
                    clear_output(wait=True)
                    print(f"🎙️ Aether: Voice essence received: '{text}'")
                
                # Process message asynchronously
                asyncio.create_task(self.process_message(text))
            else:
                with self.output_area:
                    clear_output(wait=True)
                    print("❌ Aether: No voice essence detected or transcription failed")
                    
        except Exception as e:
            with self.output_area:
                clear_output(wait=True)
                print(f"❌ Aether: Voice input disturbance - {e}")
        finally:
            self.is_listening = False
            self.audio_button.disabled = False
            self.audio_button.description = "🎙️"
            self.update_chat_display()
    
    async def process_message(self, message):
        """Process user message and get agent response"""
        self.is_listening = True
        
        with self.output_area:
            clear_output(wait=True)
            print("🌌 Aether: Weaving ethereal response...")
            
        try:
            # Add typing indicator
            response_placeholder = {'type': 'agent', 'message': '🤖 Typing...'}
            self.chat_history.append(response_placeholder)
            self.update_chat_display()
            
            # Format the message with chat history context
            chat_context = self.format_chat_history_for_agent()
            contextual_message = f"{chat_context}Current User Request: {message}"
            
            # Run the agent with full context
            with trace("aether_chat"):
                result = await Runner.run(self.agent, contextual_message)
            
            # Update with actual response
            response_placeholder['message'] = result.final_output
            self.is_listening = False
            self.update_chat_display()
            
            with self.output_area:
                clear_output(wait=True)
                print("🔊 Aether: Manifesting ethereal wisdom...")
            # Play audio response in a separate thread
            def speak_response():
                text_to_speech(result.final_output)
                with self.output_area:
                    clear_output(wait=True)
                    print("✅ Aether: Essence successfully transmitted")
                    
            threading.Thread(target=speak_response, daemon=True).start()
            
        except Exception as e:
            # Update placeholder with error
            if self.chat_history and self.chat_history[-1].get('message') == '🤖 Typing...':
                self.chat_history[-1]['message'] = f"⚠️ Ethereal Disturbance: {str(e)}"
            else:
                self.chat_history.append({'type': 'agent', 'message': f"⚠️ Ethereal Disturbance: {str(e)}"})
            
            self.is_listening = False
            self.update_chat_display()
            
            with self.output_area:
                clear_output(wait=True)
                print(f"❌ Aether: Ethereal disturbance encountered - {e}")
    
    def display(self):
        """Display the chat interface"""
        display(self.interface)

async def test_coding_agent():
    """Test function to verify CODING_AGENT uses Docker tool"""
    with trace("system"):
        result = await Runner.run(CODING_AGENT, "Write and test a python program to calculate the first 10,000 terms of this series, multiplying the total by 4: 1 - 1/3 + 1/5 - 1/7 + ...")
        print(result.final_output)

async def run_chat_interface():
    """Run the chat interface"""
    chat = ChatInterface()
    chat.display()
    
    # Keep the application running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Run the chat interface
    asyncio.run(run_chat_interface())