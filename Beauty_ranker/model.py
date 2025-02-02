import numpy as np
from PIL import Image
from pathlib import Path
import torch
from torchvision import transforms
from facenet_pytorch import MTCNN, InceptionResnetV1
from sklearn.cluster import KMeans
import shutil

class FaceClusterer:
    def __init__(self, n_clusters=2):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(device=self.device) # for detecting faces
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device) # generate face embeddings (high dimensional features representing the face)
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42) # clustering
        self.transform = transforms.Compose([
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
        ]) 

    def extract_face_embedding(self, image_path):
        """
        Loads the image and detects face using MTCNN 
        Extracts a 512 Dimensional facial embedding using InceptionResnetV1
        outputs np array representing the facial embeddings or None if no face is detected
        """
        try:
            img = Image.open(image_path).convert('RGB')
            face = self.mtcnn(img)
            
            if face is None:
                print(f"No face detected in {image_path}")
                return None
                
            with torch.no_grad():
                embedding = self.facenet(face.unsqueeze(0).to(self.device))
            
            return embedding.cpu().numpy().flatten()
            
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return None

    def process_directory(self, input_dir):
        """
        Iterates through the images in the directory 
        extracts facial embeddings for valid images 
        outputs an array of facial embeddings 
        list of valid image paths. 
        """
        embeddings = []
        valid_paths = []
        
        input_dir = Path(input_dir)
        image_paths = list(input_dir.glob('*.jpg')) + list(input_dir.glob('*.png'))
        
        for img_path in image_paths:
            embedding = self.extract_face_embedding(img_path)
            if embedding is not None:
                embeddings.append(embedding)
                valid_paths.append(img_path)
                
        return np.array(embeddings), valid_paths

    def cluster_images(self, input_dir, output_dir):
        """
        input dir is image dataset and output dir is where the clusters will be saved
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("Extracting facial embeddings...")
        embeddings, valid_paths = self.process_directory(input_dir)
        
        if len(embeddings) == 0:
            print("No valid faces found in the input directory")
            return
        
        print("Performing clustering...")
        clusters = self.kmeans.fit_predict(embeddings)

        for cluster_idx in range(self.kmeans.n_clusters):
            cluster_dir = output_dir / f"cluster_{cluster_idx}"
            cluster_dir.mkdir(exist_ok=True)
            
            cluster_indices = np.where(clusters == cluster_idx)[0]

            for idx in cluster_indices:
                src_path = valid_paths[idx]
                dst_path = cluster_dir / src_path.name
                shutil.copy2(src_path, dst_path)
                
        print(f"Clustering complete. Images organized into {self.kmeans.n_clusters} clusters.")

if __name__ == "__main__":
    clusterer = FaceClusterer(n_clusters=2)
    clusterer.cluster_images(
        input_dir="data",
        output_dir="clusters"
    )