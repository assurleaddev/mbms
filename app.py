from flask import Flask, render_template, request, Response
from main import run
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit_prompt', methods=['POST'])
def submit_prompt():
    data = request.get_json()
    message = data.get('message', '')
    
    def generate_responses():
        # First response - processing indication
        yield f"data: {json.dumps({'text': 'Analyzing your location query...'})}\n\n"
        
        try:
            # Run the crew and get the output
            crew_output = run(message)
                            
            # Final response with text, geojson, and map_commands
            final_response = {
                'text': crew_output['text'],
                'geojson': crew_output['geojson'],
                'map_commands': crew_output['map_commands'],
                'final': True
            }

        except Exception as e:
            print(f"Error running crew: {e}")
            final_response = {
                'text': 'Sorry, there was an error processing your request.',
                'geojson': None,
                'map_commands': None,
                'final': True
            }
        
        yield f"data: {json.dumps(final_response)}\n\n"
        
        # Signal end of stream
        yield f"data: [DONE]\n\n"
    
    return Response(
        generate_responses(),
        mimetype='text/plain',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )


def main():
    """Run the Location AI demo Flask application."""
    print("🗺️  Starting Location AI Demo...")
    print("📍 Open your browser to: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=True
    )

if __name__ == '__main__':
    main()