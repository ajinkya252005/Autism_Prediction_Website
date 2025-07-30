# Necessary libraries
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

# Loading dataset
ch = pd.read_csv(r"Autism-Child-Data.csv", na_values=['?'])
adu = pd.read_csv(r"Autism-Adult-Data.csv", na_values=['?'])

# Children
ch.isnull().sum()
adu.isnull().sum()

# Imputing missing values of categorical features with mode
imputer_mode = SimpleImputer(missing_values=np.nan, strategy='most_frequent')

ch.age = imputer_mode.fit_transform(ch.age.values.reshape(-1,1))[:,0]
ch.ethnicity = imputer_mode.fit_transform(ch.ethnicity.values.reshape(-1,1))[:,0]
ch.relation = imputer_mode.fit_transform(ch.relation.values.reshape(-1,1))[:,0]

adu.ethnicity = imputer_mode.fit_transform(adu.ethnicity.values.reshape(-1,1))[:,0]
adu.relation = imputer_mode.fit_transform(adu.relation.values.reshape(-1,1))[:,0]

# Imputing missing values of numerical features with mean
imputer_mode = SimpleImputer(missing_values=np.nan, strategy='mean')

ch.age = imputer_mode.fit_transform(ch.age.values.reshape(-1,1))[:,0]
adu.age = imputer_mode.fit_transform(adu.age.values.reshape(-1,1))[:,0]

# Since age of toddlers are represented in months, age(in years) of children, adolescents and adults is converted to age in months.
ch.rename(columns = {'age':'Age_Mons'}, inplace = True)
adu.rename(columns = {'age':'Age_Mons'}, inplace = True)

ch['Age_Mons'] = ch['Age_Mons']*12
adu['Age_Mons'] = adu['Age_Mons']*12

# Making classes of categorical variables same for all datasets
adu['ethnicity'] = adu['ethnicity'].replace('Others','others')

ch["relation"] = ch["relation"].replace('self','Self')

# Adding a new field that represents the age group
ch['Age_group'] = 'Children'
adu['Age_group'] = 'Adults'

# Combining the dataset of children and adults to a single dataset
frames = [ch,adu]
final = pd.concat(frames)

# Imputing missing values
imputer_mode = SimpleImputer(missing_values=np.nan, strategy='most_frequent')

final.contry_of_res = imputer_mode.fit_transform(final.contry_of_res.values.reshape(-1,1))[:,0]
final.used_app_before = imputer_mode.fit_transform(final.used_app_before.values.reshape(-1,1))[:,0]

final.describe()
final.shape

shuffled_data = final.sample(frac=1,random_state=4)
ASD_data = shuffled_data.loc[shuffled_data['Class/ASD'] == 'YES']
non_ASD_data = shuffled_data.loc[shuffled_data['Class/ASD'] == 'NO'].sample(n=666)
final= pd.concat([ASD_data, non_ASD_data])

# Split the data into features and target label
raw_target= final['Class/ASD']
raw_features = final[['A1_Score','A2_Score','A3_Score','A4_Score','A5_Score','A6_Score','A7_Score','A8_Score','A9_Score','A10_Score','Age_Mons', 'gender', 'ethnicity', 'jundice', 'austim', 'contry_of_res', 'result','relation']]

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
num_features = ['Age_Mons', 'result']

features_minmax_transform = pd.DataFrame(data = raw_features)
features_minmax_transform[num_features] = scaler.fit_transform(raw_features[num_features])

features_minmax_transform.head()

# Grouping countries and relations into broader categories **only during training**
features_minmax_transform['contry_of_res'] = features_minmax_transform['contry_of_res'].apply(lambda x: 'Other' if x not in ['United States', 'United Kingdom', 'India'] else x)
features_minmax_transform['relation'] = features_minmax_transform['relation'].apply(lambda x: 'Other' if x not in ['Parent', 'Self', 'Relative'] else x)

features = pd.get_dummies(features_minmax_transform)
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
target = le.fit_transform(raw_target)

def model_report(y_act, y_pred):
    from sklearn import metrics
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, cohen_kappa_score, roc_curve, auc, log_loss
    print("Accuracy = ", accuracy_score(y_act, y_pred))
    print("Precision = " ,precision_score(y_act, y_pred))
    print(r"Recall\Sensitivity = " ,recall_score(y_act, y_pred))
    confusion = metrics.confusion_matrix(y_act, y_pred)
    #[row, column]
    TP = confusion[1, 1]
    TN = confusion[0, 0]
    FP = confusion[0, 1]
    FN = confusion[1, 0]
    specificity = TN / (TN + FP)
    #print("Specificity = " ,specificity)
    print("F1 Score = " ,f1_score(y_act, y_pred))
    false_positive_rate, true_positive_rate, thresholds = roc_curve(y_act, y_pred)
    pass

X = features
y = target
print("Model expects these features:")
print(X.columns)

from sklearn.feature_selection import SelectKBest 
from sklearn.feature_selection import chi2  
chi2_features = SelectKBest(chi2,k=75)
fit= chi2_features.fit(X, y)
scores = pd.DataFrame(fit.scores_)
columns = pd.DataFrame(features.columns)
featureScores = pd.concat([columns,scores],axis=1)
featureScores.columns = ['Features','Score']
#print(featureScores.nlargest(50,'Score')) 

from sklearn.feature_selection import SelectKBest 
from sklearn.feature_selection import chi2  
# 700 features with highest chi-squared statistics are selected 
chi2_features = SelectKBest(chi2,k=75)
X = chi2_features.fit_transform(X, y)
y = target

# Splitting the data into train test split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20, random_state = 42)
from sklearn.model_selection import RandomizedSearchCV

C = [int(x) for x in np.linspace(start = 1, stop = 20, num = 10)]
kernel = ['linear', 'poly', 'rbf', 'sigmoid']
degree = [int(x) for x in np.linspace(start = 1, stop = 10, num = 10)]

random_grid = {'C':C,
               'kernel':kernel,
               'degree':degree}
#print(random_grid)

from sklearn.svm import SVC
svc = SVC()
svc_randomcv=RandomizedSearchCV(estimator= svc, param_distributions=random_grid, n_iter=100, cv=5, verbose=0,
                               random_state=100,n_jobs=-1)
# Fit the randomized model
svc_randomcv.fit(X_train,y_train)

# Use the best hyperparameters found or the specified ones
svc = SVC(kernel='linear', degree=3, C=13, probability=True)  # Added probability=True for better SHAP values
svc.fit(X_train, y_train)

y_pred_svc = svc.predict(X_test)
model_report(y_test, y_pred_svc)

# Recommendation Part
def generate_personalized_report(name, instance_index, raw_answers=None):
    # Get feature values (answers) for this instance
    instance = X_test.iloc[instance_index] if hasattr(X_test, 'iloc') else X_test[instance_index]
    
    # Define a mapping for question descriptions (replace with actual descriptions)
    question_descriptions = {
        'A1': 'noticing small sounds when others do not',
        'A2': 'usually concentrating more on the whole picture rather than small details',
        'A3': 'finding it easy to do more than one thing at once',
        'A4': 'if there is an interruption, can switch back to what you were doing quickly',
        'A5': 'finding it easy to "read between the lines" when someone is talking to you',
        'A6': 'knowing how to tell if someone listening to you is getting bored',
        'A7': 'finding it difficult to work out people\'s intentions',
        'A8': 'finding it difficult to make new friends',
        'A9': 'enjoying social occasions',
        'A10': 'finding it hard to work out what other people are thinking or feeling'
    }

    # Define recommendations based on AQ questions
    recommendation_map = {
        'A1': {
            1: "Consider sensory training exercises to help manage auditory sensitivity. This might include gradual exposure to different environments with varying noise levels.",
            0: "Your normal auditory processing is a strength. Continue to maintain balanced sensory environments."
        },
        'A2': {
            1: "Practice focusing on details through activities like puzzles or detailed artwork to balance your tendency to see the whole picture.",
            0: "Work on seeing the bigger picture through activities that require holistic thinking like strategic games or system mapping."
        },
        'A3': {
            1: "Your ability to multitask is a strength. Continue to utilize this in your daily activities.",
            0: "Practice single-tasking with full attention, then gradually introduce secondary tasks to improve multitasking abilities."
        },
        'A4': {
            1: "Your ability to resume tasks after interruption is a strength. Continue to apply this skill in structured environments.",
            0: "Practice task-switching exercises and use techniques like pomodoro method to build task resumption skills."
        },
        'A5': {
            1: "Continue to leverage your ability to understand implied meanings in communication.",
            0: "Consider practicing contextual interpretation through reading literary texts with metaphors and discussing them with others."
        },
        'A6': {
            1: "Your social attentiveness is a strength. Continue to observe and respond to social cues.",
            0: "Practice recognizing boredom signals through social skills training or by watching and analyzing social interactions in media."
        },
        'A7': {
            1: "Work with a therapist on theory of mind exercises to better understand others' intentions.",
            0: "Your ability to understand others' intentions is a strength. Continue to use this in social situations."
        },
        'A8': {
            1: "Consider structured social activities based on your interests to practice friendship-building skills.",
            0: "Your social connection skills are a strength. Continue to use these skills to build and maintain relationships."
        },
        'A9': {
            1: "Your enjoyment of social occasions is a strength. Continue to engage in social activities that you find pleasant.",
            0: "Start with small, structured social interactions in environments where you feel comfortable, gradually expanding your comfort zone."
        },
        'A10': {
            1: "Consider emotion recognition training or working with a therapist on empathy-building exercises.",
            0: "Your emotional intelligence is a strength. Continue to apply this in your interpersonal relationships."
        }
    }

    # Generate personalized report statements
    print(f"\n--- Personalized Analysis Report for {name} ---\n")
    
    # Get answers from raw_answers if provided, otherwise use instance values
    answers = {}
    if raw_answers is not None:
        answers = raw_answers
    else:
        for idx, row in enumerate(instance):
            feature = features.columns[idx]
            if feature.startswith('A') and feature.endswith('_Score'):
                question = feature.split('_')[0]
                answers[question] = int(row)
    
    # Generate statements for each question sequentially from A1 to A10
    for question in sorted(answers.keys()):
        answer = answers[question]
        description = question_descriptions.get(question, 'unknown question')
        recommendation = recommendation_map.get(question, {}).get(answer, 'Consider consulting with a specialist for personalized guidance.')
        
        statement = (
            f"{name}, your response to question {question} "
            f"({description}) was {answer}. "
            f"\nRecommendation: {recommendation}."
        )
        
        print(statement)
        print()
    
    # Add summary and disclaimer with improved wording
    print("\n--- Summary ---")
    print("This analysis is based on your responses to the Autism Spectrum Quotient (AQ) questions.")
    print("Disclaimer: This analysis is for informational purposes only and not a clinical diagnosis.")
    print("Please consult with a qualified healthcare professional for proper evaluation and guidance.")

# Example usage
if __name__ == "__main__":
    # Example of using the function
    generate_personalized_report(
        name="John", 
        instance_index=0,
        # Optionally provide raw answers if not directly available from X_test
        # raw_answers={'A1': 1, 'A2': 0, 'A3': 0, 'A4': 1, 'A5': 0, 'A6': 0, 'A7': 1, 'A8': 1, 'A9': 0, 'A10': 1}
    )

import joblib

# Save the trained model as a .pkl file
joblib.dump(svc, 'autism_model.pkl')

print("Model saved successfully!")