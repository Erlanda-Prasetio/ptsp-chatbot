"""
Dataset Configuration Manager
================================

Manages different dataset configurations for testing:
- NEW: Only new dataset (data_oss/)
- OLD: Only old dataset (scraped_dpmptsp/)
- COMBINED: Old + New dataset (both)

Usage:
    from config_datasets import get_dataset_config
    config = get_dataset_config('OLD')
    print(config.table_name)  # 'documents_old'
"""

from dataclasses import dataclass
from typing import Literal

DatasetType = Literal['NEW', 'OLD', 'COMBINED']


@dataclass
class DatasetConfig:
    """Configuration for a dataset variant"""
    name: str
    dataset_type: DatasetType
    table_name: str  # Supabase table name
    description: str
    source_dirs: list  # Directories to ingest from
    
    def __str__(self):
        return f"{self.name} ({self.dataset_type}): {self.description}"


# Dataset Configurations
DATASET_CONFIGS = {
    'NEW': DatasetConfig(
        name='New Dataset',
        dataset_type='NEW',
        table_name='documents',  # Keep original
        description='New dataset only (data_oss/)',
        source_dirs=['data/data_oss'],
    ),
    'OLD': DatasetConfig(
        name='Old Dataset',
        dataset_type='OLD',
        table_name='documents_old',
        description='Old dataset only (scraped_dpmptsp/)',
        source_dirs=['data/scraped_dpmptsp'],
    ),
    'COMBINED': DatasetConfig(
        name='Combined Dataset',
        dataset_type='COMBINED',
        table_name='documents_combined',
        description='Combined old + new dataset',
        source_dirs=['data/scraped_dpmptsp', 'data/data_oss'],
    ),
}


def get_dataset_config(dataset_type: DatasetType) -> DatasetConfig:
    """Get configuration for a specific dataset type"""
    if dataset_type not in DATASET_CONFIGS:
        raise ValueError(
            f"Unknown dataset type: {dataset_type}. "
            f"Available: {', '.join(DATASET_CONFIGS.keys())}"
        )
    return DATASET_CONFIGS[dataset_type]


def list_datasets():
    """Print available datasets"""
    print("\n" + "="*70)
    print("AVAILABLE DATASETS")
    print("="*70)
    for key, config in DATASET_CONFIGS.items():
        print(f"\n{key}:")
        print(f"  Table Name: {config.table_name}")
        print(f"  Description: {config.description}")
        print(f"  Source Dirs: {', '.join(config.source_dirs)}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    list_datasets()
    
    # Example usage
    print("\nExample - Getting OLD dataset config:")
    config = get_dataset_config('OLD')
    print(f"  Table: {config.table_name}")
    print(f"  Sources: {config.source_dirs}")
