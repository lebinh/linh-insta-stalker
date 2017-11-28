import datetime

import gsheet
import instagram

DOC_NAME = 'Linh Insta Test'
SHEET_NAME = 'Sheet1'
USERNAME_COL = 'IG Username'
FOLLOWERS_COL = 'Followers'
LIKES_COL = 'Likes'
COMMENTS_COL = 'Comments'
UPDATED_COL = 'Last Updated'


def main():
    client = gsheet.connect('client_secret.json')
    sheet = gsheet.TrackingSheet(client, doc_name=DOC_NAME, sheet_name=SHEET_NAME,
                                 username_col=USERNAME_COL, follower_col=FOLLOWERS_COL,
                                 likes_col=LIKES_COL, comments_col=COMMENTS_COL, updated_col=UPDATED_COL)
    today = datetime.date.today().isoformat()
    for record in sheet.records():
        try:
            user = instagram.User(record.username)
            record.update(followers=user.followers_count,
                          likes=user.average_likes_recently,
                          comments=user.average_comments_recently,
                          updated=today)
        except Exception as e:
            record.update(updated='Error: {}'.format(e))


if __name__ == '__main__':
    main()
