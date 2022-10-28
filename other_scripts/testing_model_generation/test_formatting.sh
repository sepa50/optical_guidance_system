python "..\dataset_formatter.py" --drone ".\test_processed_images\drone" --sat ".\test_processed_images\sat" --outdir ".\test_formatted_dataset"

python "..\train_test_split.py" --input_dir ".\test_formatted_dataset" --output_dir ".\test_split_dataset" --test_size 20