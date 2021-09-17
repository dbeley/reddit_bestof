import setuptools
import reddit_bestof

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="reddit_bestof",
    version=reddit_bestof.__version__,
    author="dbeley",
    author_email="dbeley@protonmail.com",
    description="Create and post reddit BestOf reports.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dbeley/reddit_bestof",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["reddit_bestof=reddit_bestof.__main__:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=["requests", "pandas", "praw", "tqdm"],
)
