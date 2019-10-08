#pragma parseroption -p-
#define public

#define FileHandle
#define FileLine
#define FileName
#define Result
#sub ProcessFileLine
  #define FileLine = FileRead(FileHandle)
  #expr Result = Result + FileLine
#endsub
#sub ProcessFile
  #for {FileHandle = FileOpen(FileName); \
    FileHandle && !FileEof(FileHandle); ""} \
    ProcessFileLine
  #if FileHandle
    #expr FileClose(FileHandle)
  #endif
#endsub

#define ReadFileAsStr(str AFileName) \
  Result = '', \
  FileName = AFileName, \
  ProcessFile, \
  Result

#define GetAppVersion(str VersionFileName) /* Result = "__version__ = 'DDDD.DD'" */ \
  ReadFileAsStr(VersionFileName), \
  Result = Copy(Result, Pos("'", Result) + 1), \
  Result = Copy(Result, 1, Pos("'", Result) - 1), \
  Result

#pragma parseroption -p+
