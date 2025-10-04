
    """Update conversation file with SLM response"""
    conversation_data = load_conversation_data(filepath)
    conversation_data['slm_response'] = response
    
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(conversation_data, file, default_flow_style=False, allow_unicode=True)