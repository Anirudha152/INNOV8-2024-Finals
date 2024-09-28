import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def read_input(file_path):
    experiences = []
    skills = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("## Experience:"):
                current_section = 'experience'
            elif line.startswith("## Skills:"):
                current_section = 'skills'
            elif current_section == 'experience' and line.startswith('-'):
                experiences.append(line[1:].strip())
            elif current_section == 'skills' and line.startswith('-'):
                skills.append(line[1:].strip())
            if line.startswith("## Sector:"):
                break
    
    return experiences, skills

# Function to split experience into heading and description based on "::"
def split_experience(experiences):
    split_experiences = []
    for experience in experiences:
        # Check if "::" exists to split heading and description
        if '::' in experience:
            parts = experience.split('::')
            heading = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ''
            split_experiences.append((heading, description))
        else:
            split_experiences.append((experience, ''))  # No description present
    
    return split_experiences

# Function to remove stopwords from text
def remove_stopwords(text):
    # Tokenize the text and remove stopwords
    tokens = re.findall(r'\w+', text.lower())  # Find all words
    filtered_tokens = [word for word in tokens if word not in ENGLISH_STOP_WORDS]
    return ' '.join(filtered_tokens)

# Function to process experiences and skills by removing stopwords
def preprocess_data(experiences, skills):
    processed_experiences = [(remove_stopwords(exp[0]), remove_stopwords(exp[1])) for exp in experiences]
    processed_skills = [remove_stopwords(skill) for skill in skills]
    return processed_experiences, processed_skills

# Function to compute relevance scores for each skill against each experience
def compute_relevance_scores(file_path):
    # Load the pre-trained model
    model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")

    # Read experiences and skills
    experiences, skills = read_input(file_path)
    
    # Split experiences into heading and description
    split_experiences = split_experience(experiences)

    # Remove stopwords from experiences and skills
    processed_experiences, processed_skills = preprocess_data(split_experiences, skills)

    # Create embeddings for skills and combined experience (heading + description)
    experience_texts = [' '.join(exp) for exp in processed_experiences]
    experience_embeddings = model.encode(experience_texts, convert_to_tensor=True)
    skill_embeddings = model.encode(processed_skills, convert_to_tensor=True)

    # Calculate cosine similarity between each skill and each experience
    relevance_matrix = np.zeros((len(skills), len(experiences)))

    for i, skill_embedding in enumerate(skill_embeddings):
        similarities = util.cos_sim(skill_embedding, experience_embeddings)
        relevance_matrix[i] = similarities.cpu().numpy()

    return relevance_matrix, processed_skills, experience_texts

# Function to print the relevance matrix with RMS values and count RMS > 0.48
def print_relevance_matrix(relevance_matrix, skills, experiences):
    print(f'{"Skill":<30} | ' + ' | '.join([f"Exp {i+1}" for i in range(len(experiences))]) + ' | RMS')
    print('-' * (35 + 15 * len(experiences) + 10))  # Adjust the width for RMS column
    
    rms_above_threshold = 0  # Initialize counter for RMS > 0.48
    
    for i, skill in enumerate(skills):
        scores = ' | '.join([f"{score:.4f}" for score in relevance_matrix[i]])
        rms = np.sqrt(np.mean(relevance_matrix[i]**2))  # Calculate RMS for the row
        
        if rms > 0.51:  # Check if RMS > 0.48
            rms_above_threshold += 1
        
        print(f'{skill:<30} | {scores} | {rms:.4f}')  # Print RMS for each skill
    
    print(f'\nNumber of skills with RMS > 0.51: {rms_above_threshold}')

# Function to return a list of skills with RMS > 0.51 and the combined L2 norm of their relevance scores
def get_skills_with_high_rms_and_combined_l2(relevance_matrix, skills, threshold=0.51):
    high_rms_skills = []
    combined_relevance_scores = []  # To store relevance scores for high RMS skills
    
    for i, skill in enumerate(skills):
        rms = np.sqrt(np.mean(relevance_matrix[i]**2))  # Calculate RMS for the row
        
        if rms > threshold:  # Check if RMS exceeds the threshold
            high_rms_skills.append(skill)
            combined_relevance_scores.append(relevance_matrix[i])  # Collect the relevance scores
    
    # Stack relevance scores from all high RMS skills
    combined_relevance_scores = np.concatenate(combined_relevance_scores, axis=0)
    
    # Calculate the L2 norm for all combined relevance scores
    combined_l2_norm = np.linalg.norm(combined_relevance_scores)
    
    return high_rms_skills, combined_l2_norm

# Specify your input file path
file_path = 'D:/aries/INNOV8-2.0-Finals-main/output1.txt'

# Compute relevance scores for each skill
relevance_matrix, processed_skills, experience_texts = compute_relevance_scores(file_path)

# Get the list of high RMS skills and the combined L2 norm of their relevance scores
high_rms_skills, combined_l2_norm = get_skills_with_high_rms_and_combined_l2(relevance_matrix, processed_skills)

# Return the list of high RMS skills and the combined L2 norm
print(high_rms_skills, combined_l2_norm)

