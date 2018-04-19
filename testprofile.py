import index
import cProfile, pstats, io

if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    index.index("dataset.csv", "dictionary.txt", "postings.txt")
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())