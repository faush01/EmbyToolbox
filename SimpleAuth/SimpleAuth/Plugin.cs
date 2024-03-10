using MediaBrowser.Common.Configuration;
using MediaBrowser.Common.Plugins;
using MediaBrowser.Model.Drawing;
using MediaBrowser.Model.Plugins;
using MediaBrowser.Model.Serialization;
using System;
using System.IO;


namespace SimpleAuth
{
    public class Plugin : BasePlugin<BasePluginConfiguration>, IHasThumbImage
    {

        public static Plugin Instance { get; private set; }
        public static string PluginName = "Simple Emby Auth";
        public static string PluginDescription = "Offers simple suth options";
        private Guid _id = new Guid("0f60d849-3b29-4736-bac0-25b7425ae5b1");

        public Plugin(IApplicationPaths applicationPaths, IXmlSerializer xmlSerializer) : base(applicationPaths, xmlSerializer)
        {
            Instance = this;
        }

        public Stream GetThumbImage()
        {
            var type = GetType();
            return type.Assembly.GetManifestResourceStream(type.Namespace + ".Images.thumb.png");
        }

        public ImageFormat ThumbImageFormat
        {
            get { return ImageFormat.Png; }
        }

        public override string Description
        {
            get { return PluginDescription; }
        }

        public override string Name
        {
            get { return PluginName; }
        }

        public override Guid Id
        {
            get { return _id; }
        }

    }
}
