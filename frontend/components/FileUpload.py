import streamlit as st
import os
from typing import List, Optional

class FileUpload:
    def __init__(self):
        self.uploaded_files = []
        self.MAX_FILES = 2
        self.MAX_SIZE_MB = 10
        
    def render(self) -> Optional[List]:
        """Render file upload component"""
        st.write("📄 Upload Reference Materials (Optional)")
        st.write(f"Support uploading up to {self.MAX_FILES} PDF files, each file not exceeding {self.MAX_SIZE_MB}MB")
        
        # File upload component
        uploaded_files = st.file_uploader(
            "Drag files here or click to select",
            type=["pdf"],
            accept_multiple_files=True,
            key="reference_files"
        )
        
        if uploaded_files:
            if len(uploaded_files) > self.MAX_FILES:
                st.error(f"Maximum {self.MAX_FILES} files allowed")
                return None
                
            valid_files = []
            for file in uploaded_files:
                # Check file size
                size_mb = file.size / (1024 * 1024)
                if size_mb > self.MAX_SIZE_MB:
                    st.error(f"File {file.name} exceeds size limit ({self.MAX_SIZE_MB}MB)")
                    continue
                    
                valid_files.append(file)
                st.success(f"File {file.name} uploaded successfully ({size_mb:.1f}MB)")
            
            if valid_files:
                return valid_files
                
        return None
        
    @staticmethod
    def save_uploaded_files(files: List) -> List[str]:
        """Save uploaded files and return file paths"""
        saved_paths = []
        temp_dir = "temp_uploads"
        
        # Create temporary directory
        os.makedirs(temp_dir, exist_ok=True)
        
        for file in files:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            saved_paths.append(file_path)
            
        return saved_paths 